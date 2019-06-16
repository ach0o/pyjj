class Colors:
    """ANSI Escape Code on colors for colorful stdout
    """

    RED = "\u001b[38;5;197m"
    GREEN = "\u001b[38;5;157m"
    YELLOW = "\u001b[38;5;220m"
    ORANGE = "\u001b[38;5;208m"


def msg(status: bool, message: str) -> str:
    """Return a colorize string depends on the status

    :param bool status: a status of the message
    :param str message: a message to display on the console
    :return: string
    """
    color = Colors.GREEN if status else Colors.RED
    return f"{color}{message}"


def header(title: str, message: str) -> str:
    """Return a colorize string for headers

    :param str title: a title to display on the console
    :param str message: a message to display on the console
    :return: string
    """
    return f"{title}\n{Colors.ORANGE}{message}"


def content(message: str) -> str:
    """Return a colorize string for content

    :param str message: a message to display on the console
    :return: string
    """
    return f"{Colors.YELLOW}{message}"
