from termcolor import colored


def _print_with_formatter(by_class, message, color='grey'):
    return print(colored("[{}] {}".format(by_class, message), color))


def successful(message):
    return _print_with_formatter("SUCCESSFUL", message, "green")


def info(message):
    return _print_with_formatter("INFO", message, "green")


def warning(message):
    return _print_with_formatter("WARNING", message, "yellow")


def critical(message):
    return _print_with_formatter("CRITICAL", message, "red")
