class Colors:
    RED = "\u001b[91m"
    GREEN = "\u001b[92m"


def msg(division, status, message) -> str:
    color = Colors.GREEN if status else Colors.RED
    return f"{color}[{division:^10}] {message}"
