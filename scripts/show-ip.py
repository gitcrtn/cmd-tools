import click

from lib.net_tools import NetTools


@click.command()
@click.option('--nic', default='')
def main(nic):
    result = NetTools().get_ip(nic)
    if type(result) == str:
        print(result)
        return
    print('\n'.join([
        '%s%s%s' % (v['nic'], v['spacer'], v['ip'])
        for v in result]))

if __name__ == '__main__':
    main()