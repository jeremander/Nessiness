import datetime
from pathlib import Path
import shlex
import shutil
import sys

from invoke import task
from invoke.main import program
from pelican import main as pelican_main
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file


SETTINGS_FILE_BASE = 'pelicanconf.py'
SETTINGS = {}
SETTINGS.update(DEFAULT_CONFIG)
LOCAL_SETTINGS = get_settings_from_file(SETTINGS_FILE_BASE)
SETTINGS.update(LOCAL_SETTINGS)

DEPLOY_PATH = SETTINGS['OUTPUT_PATH']

CONFIG = {
    'settings_base': SETTINGS_FILE_BASE,
    'settings_publish': 'publishconf.py',
    'site_name': 'nessiness.com',
    # Output path. Can be absolute or relative to tasks.py. Default: 'output'
    'deploy_path': DEPLOY_PATH,
    # Github Pages configuration
    'github_pages_branch': 'gh-pages',
    'commit_message': f"'Publish site on {datetime.date.today().isoformat()}'",
    # Host and port for `serve`
    'host': 'localhost',
    'port': 8000,
}

def log(msg):
    print(msg, file=sys.stderr)


@task
def clean(c):
    """Remove generated files"""
    deploy_path = Path(CONFIG['deploy_path'])
    if deploy_path.is_dir():
        log(f'Cleaning {deploy_path.resolve()}')
        shutil.rmtree(deploy_path)
        deploy_path.mkdir()
    else:
        log(f'ERROR: {deploy_path} is not a directory')

@task
def build(c):
    """Build local version of site"""
    pelican_run('-s {settings_base}'.format(**CONFIG))
    log(f'Built site to {DEPLOY_PATH}')

@task
def rebuild(c):
    """`build` with the delete switch"""
    pelican_run('-d -s {settings_base}'.format(**CONFIG))
    log(f'Built site to {DEPLOY_PATH}')

@task
def regenerate(c):
    """Automatically regenerate site upon file modification"""
    pelican_run('-r -s {settings_base}'.format(**CONFIG))

@task
def serve(c):
    """Serve site at http://$HOST:$PORT/ (default is localhost:8000)"""

    class AddressReuseTCPServer(RootedHTTPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(
        CONFIG['deploy_path'],
        (CONFIG['host'], CONFIG['port']),
        ComplexHTTPRequestHandler)

    log('Serving at {host}:{port} ...'.format(**CONFIG))
    server.serve_forever()

@task
def reserve(c):
    """`build`, then `serve`"""
    build(c)
    serve(c)

@task
def preview(c):
    """Build production version of site"""
    pelican_run('-s {settings_publish}'.format(**CONFIG))
    log(f'Built site with production settings to {DEPLOY_PATH}')

@task
def livereload(c):
    """Automatically reload browser tab upon file modification."""
    from livereload import Server
    build(c)
    server = Server()
    # Watch the base settings file
    server.watch(CONFIG['settings_base'], lambda: build(c))
    # Watch content source files
    content_file_extensions = ['.md', '.rst']
    for extension in content_file_extensions:
        content_blob = '{0}/**/*{1}'.format(SETTINGS['PATH'], extension)
        server.watch(content_blob, lambda: build(c))
    # Watch the theme's templates and static assets
    theme_path = SETTINGS['THEME']
    server.watch('{}/templates/*.html'.format(theme_path), lambda: build(c))
    static_file_extensions = ['.css', '.less', '.js']
    for extension in static_file_extensions:
        static_file = '{0}/static/**/*{1}'.format(theme_path, extension)
        server.watch(static_file, lambda: build(c))
    server.watch('pelicanconf.py', lambda: build(c))
    # Serve output path on configured host and port
    server.serve(host=CONFIG['host'], port=CONFIG['port'], root=CONFIG['deploy_path'])


# @task
# def publish(c):
#     """Publish to production via rsync"""
#     pelican_run('-s {settings_publish}'.format(**CONFIG))
#     c.run(
#         'rsync --delete --exclude ".DS_Store" -pthrvz -c '
#         '-e "ssh -p {ssh_port}" '
#         '{} {ssh_user}@{ssh_host}:{ssh_path}'.format(
#             CONFIG['deploy_path'].rstrip('/') + '/',
#             **CONFIG))

@task
def gh_pages(c):
    """Publish to GitHub Pages"""
    preview(c)
    c.run('ghp-import -c {site_name} -b {github_pages_branch} '
          '-m {commit_message} '
          '{deploy_path} -p'.format(**CONFIG))
    log(f"Pushed to {CONFIG['github_pages_branch']}")

@task(help={
    'force': 'suppress user confirmation',
    'dry_run': 'do not update records, just show what would happen',
})
def atproto_sync(c, force=False, dry_run=False):
    """Upload new articles to ATProto PDS."""
    from atproto.sync_articles import sync_articles
    sync_articles(prompt=not force, dry_run=dry_run)

def pelican_run(cmd):
    cmd += ' ' + program.core.remainder  # allows to pass-through args to pelican
    pelican_main(shlex.split(cmd))
