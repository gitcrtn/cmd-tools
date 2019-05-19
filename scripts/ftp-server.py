import os

import click
from pyftpdlib import authorizers, handlers, servers


def start_ftp_server(host, port, user, password, root_dir):
    auth = authorizers.DummyAuthorizer()
    auth.add_user(user, password, root_dir, perm='elradfmwMT')

    handler = handlers.FTPHandler
    handler.authorizer = auth

    server = servers.FTPServer((host, port), handler)
    server.serve_forever()


@click.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=60021)
@click.option('--user', default='user')
@click.option('--password', default='password')
@click.option('--dir', 'root_dir', default=os.getcwd())
def main(host, port, user, password, root_dir):
    print('Root Dir: ' + root_dir)
    start_ftp_server(host, port, user, password, root_dir)


if __name__ == '__main__':
    main()