import re
from urllib.parse import urlparse


def reformat_url(url: str) -> str:
    """Reformat url

    :param str url: user input url
    :exception: ValueError when url is not valid or malformed
    :return: a reformatted url
    """
    um = re.match(r"(http[s]?://)?(w{3}\.)?(.*)", url)
    if not um or not um.group(3):
        raise ValueError(f"Invalid URL: {url}")

    http, www, loc = um.groups()

    if not http:
        return f"http://{url}"
    return url


def validate_url(url: str):
    """Validate url using the structure below:
        scheme://netloc/path;parameters?query#fragment

    :param str url: user input url
    :return: a valid url
    """
    _url = reformat_url(url)
    up = urlparse(_url)
    if up.scheme and up.netloc:
        return _url
    else:
        raise ValueError(f"Invalid URL: {_url}")
