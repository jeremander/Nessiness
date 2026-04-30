#!/usr/bin/env python3

from collections.abc import Mapping
import datetime
from functools import cache
import json
import os
from pathlib import Path
import re
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
BSKY_POST_NSID = 'app.bsky.feed.post'
BSKY_EMBED_NSID = 'app.bsky.embed.external'
BSKY_REF_KEY = 'bskyPostRef'


def log(msg: str) -> None:
    print(msg, file=sys.stderr)

def get_var(context: Mapping[str, Any], name: str) -> str:
    if (value := context.get(name)) is None:
        raise ValueError(f'{name} is required')
    return value

def date_to_string(dt: datetime.datetime) -> str:
    """Converts a datetime to a canonical string for ATProto records."""
    return dt.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def get_atproto_registry() -> dict[str, Any]:
    path = Path(get_var(SETTINGS, 'ATPROTO_REGISTRY_PATH'))
    log(f'Loading ATProto registry from {path}')
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_atproto_registry(registry: dict[str, Any]) -> None:
    path = Path(get_var(SETTINGS, 'ATPROTO_REGISTRY_PATH'))
    log(f'Loading ATProto registry to {path}')
    with open(path, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    log(f'Wrote registry to {path}')

def prompt_yes_no(msg: str) -> bool:
    return input(f'{msg} [y/n] ').lower().startswith('y')

@cache
def get_client() -> Client:
    did = get_var(SETTINGS, 'ATPROTO_DID')
    return Client.new(did)

def authenticate_client(client: Client) -> None:
    if not client.is_authenticated():
        log(f'Logging into PDS with {client.session.repo.did}')
        load_dotenv()  # load password
        password = get_var(os.environ, 'ATPROTO_APP_PASSWORD')
        client.authenticate(password=password)

def build_facets(text: str) -> list[dict[str, Any]]:
    facets = []
    for match in re.finditer(r'#(\w+)', text):
        tag = match.group(1)
        # convert char offsets to byte offsets
        byte_start = len(text[:match.start()].encode())
        byte_end = len(text[:match.end()].encode())
        facets.append({
            'index': {'byteStart': byte_start, 'byteEnd': byte_end},
            'features': [{'$type': 'app.bsky.richtext.facet#tag', 'tag': tag}]
        })
    return facets

def document_record_to_bsky_post(record: dict[str, Any]) -> dict[str, Any]:
    url = get_var(SETTINGS, 'PROD_URL') + record['path']
    description = record['description']
    embed = {
        '$type': BSKY_EMBED_NSID,
        'external': {
            'uri': url,
            'title': record['title'],
            'description': description,
        }
    }
    return {
        'tags': record['tags'],
        'text': description,  # TODO: include the tags as hashtag facets?
        'embed': embed,
        'langs': ['en'],
        # 'facets': None,
        'createdAt': date_to_string(datetime.datetime.now()),
    }

def update_bsky_posts(registry: dict[str, Any], *, prompt: bool = True, dry_run: bool = False) -> None:
    has_changed = False
    for (rkey, record) in registry.items():
        if BSKY_REF_KEY in record:
            continue
        do_post = (not prompt) or prompt_yes_no(f'\tPost to Bluesky for {rkey}?')
        if not do_post:
            continue
        post = document_record_to_bsky_post(record)
        if dry_run:
            log(json.dumps(post, indent=2, ensure_ascii=True))
        else:
            client = get_client()
            authenticate_client(client)
            response = client.create_record(BSKY_POST_NSID, post)
            post_ref = {'uri': response['uri'], 'cid': response['cid']}
            record['bskyPostRef'] = post_ref
            has_changed = True
    if has_changed:
        save_atproto_registry(registry)
    else:
        log('No changes to registry')

def sync_articles(*, prompt: bool = True, dry_run: bool = False) -> None:
    """Uploads new articles to ATProto PDS."""
    if dry_run:
        log('Doing dry run (will not actually update any records)')
    registry = get_atproto_registry()
    num_articles = len(registry)
    log(f'{num_articles} article(s) in registry')
    update_bsky_posts(registry, prompt=prompt, dry_run=dry_run)
    client = get_client()
    # check which records are new
    pds_records = client.list_records('site.standard.document')
    pds_rkeys = {record.uri.split('/')[-1] for record in pds_records}
    pub_prefix = get_var(SETTINGS, 'ATPROTO_PUB_PREFIX')
    # only include rkeys tied to the site's publication
    pds_rkeys = {rkey for rkey in pds_rkeys if rkey.startswith(f'{pub_prefix}:')}
    log(f'{len(pds_rkeys)} article(s) for {pub_prefix} in PDS')
    # NOTE: we check for new articles and deleted articles, but we don't check if any article metadata has *changed*.
    # Records do not store the content, so an article may change and its record will still point to the updated page.
    # It's possible we might want to update other metadata like the description or cover image, but we do not support
    # that for now.
    new_records = [(rkey, record) for (rkey, record) in registry.items() if (rkey not in pds_rkeys)]
    new_records.sort(key=lambda pair: pair[1]['publishedAt'])
    # log(f'{num_in_pds} of {num_articles} published articles are in PDS')
    missing_rkeys = {rkey for rkey in pds_rkeys if (rkey not in registry)}
    num_to_create = len(new_records)
    num_to_delete = len(missing_rkeys)
    if max(num_to_create, num_to_delete) == 0:
        log('No articles to upload or delete.')
        return
    log(f'records to create: {num_to_create}')
    log(f'records to delete: {num_to_delete}')
    upload = (not prompt) or prompt_yes_no('Update article records in PDS?')
    if upload:
        if not dry_run:
            authenticate_client(client)
        for (rkey, record) in new_records:
            log(f'\tCreating {rkey}')
            if not dry_run:
                if record.get(BSKY_REF_KEY) is None:
                    # NOTE: if this field is None, omit it from the record
                    record.pop(BSKY_REF_KEY, None)
                client.create_record(DOCUMENT_NSID, record, rkey)
        for rkey in missing_rkeys:
            log(f'\tDeleting {rkey}')
            if not dry_run:
                client.delete_record(DOCUMENT_NSID, rkey)
        log('PDS sync successful.')
    else:
        log('Aborting PDS sync.')


if __name__ == '__main__':
    sync_articles()
