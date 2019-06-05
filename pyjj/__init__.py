import click

from .config import PyjjConfig
from .database import Database as Db


def msg(division, status, message) -> str:
    return f"\033[92m[{division}] {message}" if status else f"\033[91m[Oops!] {message}"


pass_config = click.make_pass_decorator(PyjjConfig, ensure=True)


@click.group()
@pass_config
def pyjj(config):
    """A CLI tool for bookmark management."""
    config.parse()
    config.db = Db(division=config.division)
    config.db.setup()


@pyjj.command()
@click.argument("division")
@pass_config
def use(config, division=str):
    """Switch to a different table

    :param str division: a name of the division
    """
    config.update(division=division)
    click.echo(f"Switched to {division}")


@pyjj.command()
@pass_config
def list(config):
    """Show a list of bookmarks"""
    status, urls = config.db.list_urls()
    if not status:
        click.echo(msg(config.division, status, urls))
    else:
        click.echo(f"[{config.division:^10}]")
        click.echo(f"{'ID':^7} {'URL':70} DATE")
        for id, url, date in urls:
            click.echo(f"{id:^7} {url:70} {date}")


@pyjj.command()
@click.argument("url")
@pass_config
def add(config, url):
    """Add a new bookmark"""
    result = config.db.add_url(url)
    click.echo(msg(config.division, *result))


@pyjj.command()
@click.argument("id")
@click.option("--url", help="Edit url")
@pass_config
def edit(config, url, id):
    """Edit a bookmark"""
    result = config.db.edit_url(id, url)
    click.echo(msg(config.division, *result))


@click.argument("id")
@pyjj.command()
@pass_config
def remove(config, id):
    """remove a bookmark"""
    result = config.db.remove_url(id)
    click.echo(msg(config.division, *result))


if __name__ == "__main__":
    pyjj()
