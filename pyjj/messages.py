class Colors:
    """ANSI Escape Code on colors for colorful stdout
    """

    RED = "\u001b[38;5;197m"
    GREEN = "\u001b[38;5;157m"


def msg(division: str, status: bool, message: str) -> str:
    """Return a colorize string depends on the status

    :param str division: a current division
    :param bool status: a status of the message
    :param str message: a message to display on the console
    :return: string
    """
    color = Colors.GREEN if status else Colors.RED
    return f"{color}[{division:^10}] {message}"
