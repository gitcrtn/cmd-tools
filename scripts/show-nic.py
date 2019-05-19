from lib.net_tools import NetTools


def main():
    result = NetTools().get_nic()
    print('\n'.join([
        '%s%sType:%s%sHWaddr %s' % (
            v['name'], v['nic_spacer'], v['type'], v['type_spacer'], v['hwaddr'])
        for v in result]))

if __name__ == '__main__':
    main()