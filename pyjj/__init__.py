import click
from . import database as db


class Config:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if not self._db:
            self._db = db.Database()
        return self._db


def msg(status, message) -> str:
    return f"\033[92m[Yay!] {message}" if status else f"\033[91m[Oops!] {message}"


config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@config
def pyjj(config):
    """A CLI tool for bookmark management."""
    click.echo("Hello, this is pyjj")


@pyjj.command()
@config
def list(config):
    """Show a list of bookmarks"""
    click.echo("this is pyjj list")
    c = config.db
    for url in c.list_urls():
        click.echo(url)


@pyjj.command()
@click.argument("url")
@config
def add(config, url):
    """Add a new bookmark"""
    click.echo("this is pyjj add")
    result = config.db.add_url(url)
    click.echo(msg(**result))


@pyjj.command()
@click.argument("id")
@click.option("--url", help="Edit url")
@config
def edit(config, url, id):
    """Edit a bookmark"""
    click.echo("this is pyjj edit")
    config.db.edit_url(id, url)


@pyjj.command()
def remove():
    """remove a bookmark"""
    click.echo("this is pyjj remove")


if __name__ == "__main__":
    pyjj()
