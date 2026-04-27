"""Create ATProto records conforming to standard.site Lexicons."""

import datetime
from html.parser import HTMLParser
import json
import logging
from pathlib import Path
from typing import Any

from pelican import signals
from pelican.contents import Article
from pelican.generators import ArticlesGenerator
from pelican.writers import Writer


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


_ATPROTO_REGISTRY = None


class TagStripper(HTMLParser):
    """Helper class for stripping HTML tags from text."""
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return ''.join(self._parts)


def date_to_string(dt: datetime.datetime) -> str:
    """Converts a datetime to a canonical string for ATProto records."""
    return dt.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def strip_tags(html: str) -> str:
    """Strips HTML tags from text."""
    stripper = TagStripper()
    stripper.feed(html)
    return stripper.get_text()

def get_atproto_registry_path(settings: dict[str, Any]) -> Path:
    path = settings.get('ATPROTO_REGISTRY_PATH')
    if path is None:
        raise ValueError('ATPROTO_REGISTRY_PATH is required')
    return Path(path)

def get_atproto_registry(settings: dict[str, Any]) -> dict[str, Any]:
    global _ATPROTO_REGISTRY
    if _ATPROTO_REGISTRY is None:
        path = get_atproto_registry_path(settings)
        LOGGER.info(f'Loading ATProto registry from {path}')
        if path.exists():
            with open(path) as f:
                registry = json.load(f)
        else:
            registry = {}
        LOGGER.info(f'{len(registry)} article(s) in registry')
        _ATPROTO_REGISTRY = registry
    return _ATPROTO_REGISTRY

def article_to_standard_site_record(settings: dict[str, Any], article: Article) -> dict[str, Any]:
    site_url = settings.get('ATPROTO_SITEURL')
    if site_url is None:
        raise ValueError('ATPROTO_SITEURL is required')
    date_str = date_to_string(article.date)
    record = {
        'path': '/' + article.slug,
        'site': site_url,
        'tags': [tag.name for tag in article.tags],
        'title': strip_tags(article.title),
        # TODO: content: optional inline content, e.g. with https://markpub.at
        # TODO: updatedAt (use Git history)?
        # TODO: coverImage: optional thumbnail, if in the Markdown
        # TODO: bskyPostRef: strongRef pointing to Bluesky post
        'description': strip_tags(article.summary),
        'publishedAt': date_str,
    }
    return {key: val for (key, val) in record.items() if (val is not None)}

# article_generator_write_article

def update_atproto_records(generator: ArticlesGenerator, writer: Writer) -> None:
    """Updates the local ATProto JSON registry with the current article data."""
    global _ATPROTO_REGISTRY
    settings = generator.settings
    registry = get_atproto_registry(settings)
    published_articles = [article for article in generator.articles if (article.status == 'published')]
    # TODO: post the unregistered articles only
    unregistered_articles = [article for article in published_articles if (article.url not in registry)]
    LOGGER.info(f'{len(unregistered_articles)} article(s) are unregistered')
    pub_prefix = settings.get('ATPROTO_PUB_PREFIX')
    registry = {}
    for article in published_articles:
        rkey_segments = [pub_prefix] if pub_prefix else []
        # for rkey, include the date and slug (hopefully uniquely identifies each article)
        rkey_segments += [article.date.strftime('%Y%m%d'), article.slug]
        rkey = ':'.join(rkey_segments)
        if rkey in registry:
            raise ValueError(f'duplicate document rkey {rkey!r} in ATProto registry')
        registry[rkey] = article_to_standard_site_record(settings, article)
    _ATPROTO_REGISTRY = registry
    LOGGER.info(f'Updated registry with {len(registry)} article(s)')
    path = get_atproto_registry_path(settings)
    with open(path, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    LOGGER.info(f'Wrote registry to {path}')

# TODO: post to Bluesky embedding link to post
# TODO: upload standard.site record pointing to the post

def register() -> None:
    """Registers signals from Pelican."""
    signals.article_writer_finalized.connect(update_atproto_records)
