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

ATPROTO_REGISTRY_PATH = Path('atproto_registry.json')


class TagStripper(HTMLParser):
    """Helper class for stripping HTML tags from text."""
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return ''.join(self._parts)


def strip_tags(html: str) -> str:
    """Strips HTML tags from text."""
    stripper = TagStripper()
    stripper.feed(html)
    return stripper.get_text()


def article_to_standard_site_record(settings: dict[str, Any], article: Article) -> dict[str, Any]:
    site_url = settings.get('ATPROTO_SITEURL')
    if site_url is None:
        raise ValueError('ATPROTO_SITEURL is required')
    date_str = article.date.astimezone(datetime.timezone.utc).isoformat()[:23] + 'Z'
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


def update_atproto_records(generator: ArticlesGenerator, writer: Writer) -> None:
    """Updates the local ATProto JSON registry with the current article data."""
    settings = generator.settings
    atproto_registry_path = settings.get('ATPROTO_REGISTRY_PATH')
    if atproto_registry_path is None:
        raise ValueError('ATPROTO_REGISTRY_PATH is required')
    atproto_registry_path = Path(atproto_registry_path)
    LOGGER.info(f'Loading ATProto registry from {atproto_registry_path}')
    if atproto_registry_path.exists():
        with open(atproto_registry_path) as f:
            registry = json.load(f)
    else:
        registry = {}
    LOGGER.info(f'{len(registry)} article(s) in registry')
    published_articles = [article for article in generator.articles if (article.status == 'published')]
    # TODO: post the unregistered articles only
    unregistered_articles = [article for article in published_articles if (article.url not in registry)]
    LOGGER.info(f'{len(unregistered_articles)} article(s) are unregistered')
    registry = {
        article.url: article_to_standard_site_record(settings, article) for article in published_articles
    }
    LOGGER.info(f'Updated registry with {len(registry)} article(s)')
    with open(atproto_registry_path, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    LOGGER.info(f'Wrote registry to {atproto_registry_path}')

# TODO: post to Bluesky embedding link to post
# TODO: upload standard.site record pointing to the post

def register() -> None:
    """Registers signals from Pelican."""
    signals.article_writer_finalized.connect(update_atproto_records)
