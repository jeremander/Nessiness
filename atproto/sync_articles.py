#!/usr/bin/env python3

from collections.abc import Mapping
import json
import os
from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv
from lexiform.atproto.client import Client
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file


SETTINGS_FILE_BASE = 'pelicanconf.py'
SETTINGS = {}
SETTINGS.update(DEFAULT_CONFIG)
LOCAL_SETTINGS = get_settings_from_file(SETTINGS_FILE_BASE)
SETTINGS.update(LOCAL_SETTINGS)


def log(msg: str) -> None:
    print(msg, file=sys.stderr)

def get_var(context: Mapping[str, Any], name: str) -> str:
    if (value := context.get(name)) is None:
        raise ValueError(f'{name} is required')
    return value

def get_atproto_registry() -> dict[str, Any]:
    path = Path(get_var(SETTINGS, 'ATPROTO_REGISTRY_PATH'))
    log(f'Loading ATProto registry from {path}')
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def sync_articles(*, prompt: bool = True) -> None:
    """Uploads new articles to ATProto PDS."""
    load_dotenv()  # load password
    password = get_var(os.environ, 'ATPROTO_APP_PASSWORD')
    registry = get_atproto_registry()
    num_articles = len(registry)
    log(f'{num_articles} article(s) in registry')
    did = get_var(SETTINGS, 'ATPROTO_DID')
    client = Client.new(did)
    # check which records are new
    pds_records = client.list_records('site.standard.document')
    pds_rkeys = {record.uri.split('/')[-1] for record in pds_records}
    # NOTE: we don't check if records have changed.
    # Records do not store the content, so an article may change and its record will still point to the updated page.
    # It's possible we might want to update other metadata like the description or cover image, but we do not support
    # that for now.
    new_records = [(rkey, record) for (rkey, record) in registry.items() if (rkey not in pds_rkeys)]
    new_records.sort(key=lambda pair: pair[1]['publishedAt'])
    num_in_pds = len(registry) - len(new_records)
    log(f'{num_in_pds} of {num_articles} are in PDS')
    if not new_records:
        log('No new articles to upload.')
        return
    if prompt:
        upload = input('Upload new articles? [Y/N] ').lower().startswith('y')
    else:
        upload = True
    if upload:
        log(f'Logging into PDS with {client.session.repo.did}')
        client.authenticate(password=password)
        for (rkey, record) in new_records:
            log(f'\t{rkey}')
            # client.create_record('site.standard.document', record, rkey)
        log('Upload successful.')


if __name__ == '__main__':
    sync_articles()
