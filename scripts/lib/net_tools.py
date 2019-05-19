import re
import sys
import subprocess


class NetTools(object):
    def __init__(self):
        nic_filters = {
            'v1': re.compile('^([\w\s]+)Link encap:'),
            'v2': re.compile('^(\w+): flags='),
        }
        nic_type_filters = {
            'v1': re.compile('Link encap:([\w\s]+)'),
            'v2': re.compile(''),
        }
        hwaddr_filters = {
            'v1': re.compile('HWaddr ([\w:]+)'),
            'v2': re.compile(''),
        }
        ip_filters = {
            'v1': re.compile('inet addr:(\d+)\.(\d+)\.(\d+)\.(\d+)(\s+)'),
            'v2': re.compile('inet (\d+)\.(\d+)\.(\d+)\.(\d+)(\s+)'),
        }

        self._version = self._check_net_tools_version()
        if not self._version:
            print('Error: net-tools is not installed.')
            sys.exit(1)
        
        self._nic_filter = nic_filters[self._version]
        self._nic_type_filter = nic_type_filters[self._version]
        self._hwaddr_filter = hwaddr_filters[self._version]
        self._ip_filter = ip_filters[self._version]
        self._nic_spacer_count = 10
        self._type_spacer_count = 15
    
    def get_ip(self, nic=None):
        arg_nic = nic
        current_nic = None
        results = []

        for line in self.get_ifconfig_results():
            nic = self._get_nic(line)

            if arg_nic and nic is not None and nic.strip() != arg_nic:
                continue

            if nic:
                current_nic = nic.strip()
                continue

            if not current_nic:
                continue
            
            ip = self._get_ip(line)

            if not ip:
                continue
            
            if arg_nic:
                return ip
            
            results.append({
                'nic': current_nic,
                'ip': ip,
                'spacer': self._get_spacer(current_nic),
            })
            current_nic = None
        
        return results
    
    def get_nic(self):
        if self._version == 'v2':
            print('Warning: Not implemented.')
            sys.exit(1)

        results = []

        for line in self.get_ifconfig_results():
            res = self._nic_filter.search(line)

            if not res:
                continue
            
            name = res.group(1).strip()
            type_ = self._get_nic_type(line)
            results.append({
                'name': name,
                'type': type_,
                'hwaddr': self._get_hwaddr(line),
                'nic_spacer': self._get_spacer(name),
                'type_spacer': self._get_spacer(name, type_),
            })
        
        return results

    def get_ifconfig_results(self, args=''):
        return self._get_command_results(
            'ifconfig' if not args else 'ifconfig ' + args)

    def _get_spacer(self, nic, type_=None):
        spacer_count = self._nic_spacer_count if not type_ else self._type_spacer_count
        value = nic if not type_ else type_
        delta = max(len(nic) - self._nic_spacer_count, 0) if type_ else 0
        if delta > 0:
            delta += 1
        return ' ' * max(spacer_count - len(value) - delta, 1)

    def _get_nic(self, line):
        res = self._nic_filter.search(line)
        if not res:
            return None
        return res.group(1)
    
    def _get_nic_type(self, line):
        res = self._nic_type_filter.search(line)
        if not res:
            return None
        return res.group(1).split('HWaddr')[0].strip()
    
    def _get_hwaddr(self, line):
        res = self._hwaddr_filter.search(line)
        if not res:
            return None
        return res.group(1)

    def _get_ip(self, line):
        res = self._ip_filter.search(line)
        if not res:
            return None
        return '.'.join([res.group(i+1) for i in range(4)])
        
    def _get_command_results(self, cmd):
        try:
            output = subprocess.check_output(
                cmd.split(), stderr=subprocess.STDOUT)
        except Exception as e:
            output = e.output
        return output.decode(encoding='utf-8').splitlines()

    def _check_net_tools_version(self):
        lines = self.get_ifconfig_results('--version')
        for line in lines:
            if line.startswith('net-tools 1'):
                return 'v1'
            if line.startswith('net-tools 2'):
                return 'v2'
        return None