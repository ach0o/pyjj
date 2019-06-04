import click

from .database import Database as Db


def msg(status, message) -> str:
    return f"\033[92m[Yay!] {message}" if status else f"\033[91m[Oops!] {message}"


db = Db()


@click.group()
def pyjj():
    """A CLI tool for bookmark management."""
    click.echo(f"[{db.division:^10}]")


@pyjj.command()
@click.argument("division")
def use(division=str):
    """Switch to a different table

    :param str division: a name of the division
    """
    global db
    db = Db(division=division)
    click.echo(f"Switched to {division}")


@pyjj.command()
def list():
    """Show a list of bookmarks"""
    status, urls = db.list_urls()
    if not status:
        click.echo(msg(status, urls))
    else:
        click.echo(f"{'ID':^7} {'URL':70} DATE")
        for id, url, date in urls:
            click.echo(f"{id:^7} {url:70} {date}")


@pyjj.command()
@click.argument("url")
def add(url):
    """Add a new bookmark"""
    result = db.add_url(url)
    click.echo(msg(*result))


@pyjj.command()
@click.argument("id")
@click.option("--url", help="Edit url")
def edit(url, id):
    """Edit a bookmark"""
    result = db.edit_url(id, url)
    click.echo(msg(*result))


@click.argument("id")
@pyjj.command()
def remove(id):
    """remove a bookmark"""
    result = db.remove_url(id)
    click.echo(msg(*result))


if __name__ == "__main__":
    pyjj()
