# Nessiness

## Deployment

- Use `invoke` to execute commands:
  - `--list`: List commands
  - `livereload`: Serve in dev mode (hot reloading)
  - `build`: Build local version of site
  - `gh-pages`: Publish to Github Pages
  - `atproto-sync`: Sync ATProto records

Docs for [Pelican](https://docs.getpelican.com/en/latest/index.html) and [plugins](https://docs.getpelican.com/en/latest/plugins.html).

[Flex](https://github.com/alexandrevicenzi/Flex/tree/master) theme for Pelican (currently using 2.2.0, could be tricky to update).

## ATproto Workflow

### Creating a Post

1. Write a new blog post.
1. Build the site.
    - Derive document `rkey` from unique ID of the blog post (basically URL path).
    - Use this to create AT-URI, embed this in `<link>` in page head.
1. Publish to GH Pages. Site update goes live.
1. Post to Bluesky, embedding the website link.
1. Update metadata for new blog post in the local registry.
    - Store `rkey` and `site.standard.document` record.
    - Point to:
      - `site`: AT-URI of the `site.standard.publication` record
      - `bskyPostRef`: strong ref to the Bluesky post
1. Upload `site.standard.document` record for the new post to the PDS.

### Deleting a Post

1. Delete the post.
1. Delete metadata for the post in the local registry.
1. Build & publish the site.
1. Delete `site.standard.document` record from the PDS.
1. Optionally, delete the Bluesky post manually.

### Updating a Post

1. Update the post.
1. Build & publish the site.

That's all there is to do, since the links should all persist even when content changes.
