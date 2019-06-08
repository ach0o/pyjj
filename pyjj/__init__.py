import click

from .config import PyjjConfig
from .database import Database as Db
from .messages import msg


pass_config = click.make_pass_decorator(PyjjConfig, ensure=True)


@click.group(help="A CLI tool for bookmark management")
@pass_config
def pyjj(config):
    """A CLI tool for bookmark management

    :param object config: an object with the current context
    """
    config.parse()
    config.db = Db(division=config.division)
    config.db.setup()


@pyjj.command(help="Switch to a different table")
@click.argument("division")
@pass_config
def use(config, division=str):
    """Switch to a different table

    :param object config: an object with the current context
    :param str division: a name of the division
    """
    config.update(division=division)
    click.echo(f"Switched to {division}")


@pyjj.command(help="Show a list of bookmarks")
@click.option("--tag", "-t", is_flag=True)
@pass_config
def list(config, tag):
    """Show a list of bookmarks

    :param object config: an object with the current context
    """
    status, urls = config.db.list_urls(with_tag=tag)
    if not status:
        click.echo(msg(config.division, status, urls))
    else:
        click.echo(f"[{config.division:^10}]")
        if tag:
            click.echo(f"{'ID':^7} {'URL':60} {'TAGS':20} DATE")
            for url, tags in urls:
                click.echo(f"{url[0]:^7} {url[1]:60} {','.join(tags):20} {url[2]}")
        else:
            click.echo(f"{'ID':^7} {'URL':60} DATE")
            for id, url, date in urls:
                click.echo(f"{id:^7} {url:60} {date}")


@pyjj.command(help="Add a new bookmark")
@click.argument("url")
@click.option("--tags", "-t")
@pass_config
def add(config, tags: str, url: str):
    """Add a new bookmark

    :param object config: an object with the current context
    :param str url: an url to add to the database
    """
    result = config.db.add_url(url, tags=tags.split(","))
    click.echo(msg(config.division, *result))


@pyjj.command(help="Edit a bookmark")
@click.argument("id")
@click.argument("url")
@pass_config
def edit(config, id: int, url: str):
    """Edit a bookmark

    :param object config: an object with the current context
    :param int id: an id of url to edit
    :param str url: an url to add to the database
    """
    result = config.db.get_url(id)
    if result[0]:  # Edit url as id exists
        result = config.db.edit_url(id, url)
    click.echo(msg(config.division, *result))


@pyjj.command(help="Remove a bookmark")
@click.argument("id")
@pass_config
def remove(config, id):
    """Remove a bookmark

    :param object config: an object with the current context
    :param int id: an id of url to delete
    """
    result = config.db.get_url(id)
    if result[0]:  # Remove url as id exists
        is_confirmed = click.confirm(f"Wish to delete {result[1]} ?")
        if is_confirmed:
            result = config.db.remove_url(id)
        else:
            result = (False, "aborted.")
    click.echo(msg(config.division, *result))


if __name__ == "__main__":
    pyjj()
