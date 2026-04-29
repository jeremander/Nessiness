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
DOCUMENT_NSID = 'site.standard.document'


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

def sync_articles(*, prompt: bool = True, dry_run: bool = False) -> None:
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
    pub_prefix = get_var(SETTINGS, 'ATPROTO_PUB_PREFIX')
    # only include rkeys tied to the site's publication
    pds_rkeys = {rkey for rkey in pds_rkeys if rkey.startswith(f'{pub_prefix}:')}
    log(f'{num_articles} article(s) for {pub_prefix} in PDS')
    # NOTE: we check for new articles and deleted articles, but we don't check if any article metadata has *changed*.
    # Records do not store the content, so an article may change and its record will still point to the updated page.
    # It's possible we might want to update other metadata like the description or cover image, but we do not support
    # that for now.
    new_records = [(rkey, record) for (rkey, record) in registry.items() if (rkey not in pds_rkeys)]
    new_records.sort(key=lambda pair: pair[1]['publishedAt'])
    num_in_pds = len(registry) - len(new_records)
    log(f'{num_in_pds} of {num_articles} published articles are in PDS')
    missing_rkeys = {rkey for rkey in pds_rkeys if (rkey not in registry)}
    if (not new_records) and (not missing_rkeys):
        log('No articles to upload or delete.')
        return
    if prompt:
        upload = input('Update article records in PDS? [Y/N] ').lower().startswith('y')
    else:
        upload = True
    if upload:
        if not dry_run:
            log(f'Logging into PDS with {client.session.repo.did}')
            client.authenticate(password=password)
        for (rkey, record) in new_records:
            log(f'\tCreating {rkey}')
            if not dry_run:
                client.create_record(DOCUMENT_NSID, record, rkey)
        for rkey in missing_rkeys:
            log(f'\tDeleting {rkey}')
            if not dry_run:
                client.delete_record(DOCUMENT_NSID, rkey)
        log('PDS sync successful.')


if __name__ == '__main__':
    sync_articles()
