#!/usr/bin/python3


from __future__ import print_function
import re
import socket
import argparse
from prettytable import PrettyTable

def Lookup(addr):
    if (re.search(r'^[a-z]+[-0-9a-z]+[-.0-9a-z]*$',addr, re.I)):
        try:
            return((socket.gethostbyname(addr), addr))
        except:
            return('unknown.dom',addr)
    elif (re.search(r'^([0-9]+.){3}[0-9]+$',addr)):
        for octet in addr.split('.'):
            if (int(octet) > 255):
                return('Invalid Address')
        try:
            return((addr, socket.gethostbyaddr(addr)[0]))
        except:
            return(addr,'unknown.dom')
    else:
        return("Invalid Address")

if ( __name__ == '__main__'):
    parser = argparse.ArgumentParser(description='This tool is resolve name to ip and vice versa')
    parser.add_argument('addr', action="store")
    args = parser.parse_args()
    print(Lookup(args.addr))
