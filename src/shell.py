import cmd

from fetcher import start_fetcher, stop_fetcher
from db import add_user, delete_user, list_users


class MailShell(cmd.Cmd):
    intro = "Welcome to MailShell. Type help or ? to list commands."
    prompt = "mail> "

    def __init__(self, db_path: str, key: bytes):
        super().__init__()
        self.db_path = db_path
        self.key = key

    def do_add_user(self, arg):
        """add_user <userid> <password> — Add a new user"""
        parts = arg.split()
        if len(parts) != 2:
            print("Usage: add_user <userid> <password>")
            return
        userid, password = parts
        add_user(self.db_path, userid, password, self.key)

    def do_list_users(self, arg):
        """list_users — Show all registered users"""
        users = list_users(self.db_path, self.key)
        print(users)

    def do_delete_user(self, arg):
        """delete_user <userid> — Delete a user"""
        if not arg:
            print("Usage: delete_user <userid>")
            return
        delete_user(self.db_path, arg)

    def do_start_fetcher(self, arg):
        """starts fetcher"""
        start_fetcher()

    def do_stop_fetcher(self, arg):
        """stops fetcher"""
        stop_fetcher()

    def do_exit(self, arg):
        """exit - Quit the shell"""
        return True

    def do_quit(self, arg):
        """quit - Quit the shell"""
        return self.do_exit(arg)
