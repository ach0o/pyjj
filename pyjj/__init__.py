import click

from .config import PyjjConfig
from .database import Database as Db
from .messages import msg, header, content


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
    click.echo(f"Division: {config.division}")


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
@click.option("--tag", "-t")
@pass_config
def list(config, tag: str):
    """Show a list of bookmarks

    :param object config: an object with the current context
    :param str tag: a tag of urls
    """
    status, urls = config.db.list_urls(tag=tag)
    if not status:
        click.echo(msg(config.division, status, urls))
    else:
        click.echo(header("Bookmarks", f"{'ID':^7} {'URL':60} {'TAGS':20} DATE"))
        for url, tags in urls:
            click.echo(content(f"{url[0]:^7} {url[1]:60} {','.join(tags):20} {url[2]}"))

    # TODO: Pagination


@pyjj.command(help="Add a new bookmark")
@click.argument("url")
@click.option("--tags", "-t")
@pass_config
def add(config, tags: str, url: str):
    """Add a new bookmark

    :param object config: an object with the current context
    :param str url: an url to add to the database
    """
    if tags:
        result = config.db.add_url(url, tags=tags.split(","))
    else:
        result = config.db.add_url(url)
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
@click.option("--tag", "-t")
@pass_config
def remove(config, id, tag):
    """Remove a bookmark. When given option `-t`, only the tag
    associated with the url gets removed.

    :param object config: an object with the current context
    :param int id: an id of url to delete
    :param str tag: a tag of url to delete
    """
    result = config.db.get_url(id)
    if result[0]:  # Remove url as id exists
        if tag:
            result = config.db.remove_url_tag(id, tag)
        else:
            is_confirmed = click.confirm(f"Wish to delete {result[1]} ?")
            if is_confirmed:
                result = config.db.remove_url(id)
            else:
                result = (False, "aborted.")
    click.echo(msg(config.division, *result))


@pyjj.command(help="Get a random bookmark")
@click.option("--tag", "-t")
@pass_config
def eureka(config, tag=None):
    """Get a random bookmark. When given option `-t`, returns
    a randome bookmark with the given tag.

    :param object config: an object with the current context
    :param str tag: a tag of a random url
    """
    _, url_tags = config.db.get_random_url(tag)
    url, tags = url_tags

    click.echo(header("Eureka!", f"{'ID':^7} {'URL':60} {'TAGS':20} DATE"))
    click.echo(content(f"{url[0]:^7} {url[1]:60} {','.join(tags):20} {url[2]}"))


@pyjj.command(help="Show a list of tags")
@pass_config
def tags(config):
    """Show a list of tags.

    :param object config: an object with the current context
    """
    status, tags = config.db.list_tags()
    click.echo(header("Tags", f"{'ID':^7} {'TAGS':20} DATE"))
    if status:
        for index, tag in tags:
            click.echo(content(f"{index:^7} {tag[0]:20} {tag[1]}"))


if __name__ == "__main__":
    pyjj()
