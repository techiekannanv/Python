#!/usr/bin/python3
"""
This is used to parse config file separated by any fixed character throughout the file.
"""

from os import path
import re


class Parser:

    def __init__(self):
        self.data = {}
        self.error = True

    def read(self, filename, separator='=', value_type='str', value_empty=None):

        if not path.exists(filename):
            self.error = False
            return False

        data = open(filename, 'r')
        for line in data:
            if re.match(r'\s*[a-zA-Z_]+', line):
                if not re.search(r'=', line):
                    line += '='
                line = line.rstrip()
                varname, value = line.split(separator)
                varname = varname.strip()
                value = value.strip()
                if re.search(r'^\s*$', value):
                    value = value_empty
                if value_type == 'list' and value not in (None, True):
                    value = re.findall(r'\w+', value)
                self.data[varname] = value
        return self.error


config = Parser()
if config.read('config', value_type='list'):
    for param in config.data:
        print("{} = {}".format(param, config.data[param]))
