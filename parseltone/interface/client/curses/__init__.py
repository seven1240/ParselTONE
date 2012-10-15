from getpass import getpass


def prompt_credentials():
    """
    Prompt the user to enter their credentials.

    Returns a tuple of username and password.
    """
    username = raw_input('Username: ')
    password = getpass('Password: ')
    return (username, password)

