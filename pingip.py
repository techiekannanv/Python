#!/usr/bin/python

from __future__ import print_function
import subprocess
import re
import argparse


def Ping(ip,count=3,timeout=3):
    process = subprocess.Popen("ping -c "+str(count)+" -W "+str(timeout)+" "+ip,shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output = process.communicate()
    if (output[1] != ''):
        return("Error:"+output[1].rstrip('\n'))
    for line in output[0].split('\n'):
        percentage = re.search(r'[0-9]+%',line)
        if (percentage):
            percentage = int(percentage.group().rstrip('%'))
            if ( percentage == 0 ):
                return('\033[32mAlive\033[0m')
            elif ( percentage > 0 and percentage < 100 ):
                return('PacketDrop')
            else:
                return('\033[31mDead\033[0m')

if (__name__ == '__main__'):
    parse = argparse.ArgumentParser(description="This script is used to ping the IP and provide the status")
    parse.add_argument('-f', action='store', dest='file', default=None)
    parse.add_argument('-i', action='store', dest='ip', default=None)
    parse.add_argument('-c', action='store', dest='count', default=3)
    parse.add_argument('-W', action='store', dest='timeout', default=1)
    args = parse.parse_args()
    ips = []
    if ( args.file == None and args.ip == None ):
        parse.print_help()

    if ( args.file != None ):
        with open(args.file,'r') as file:
            for line in file:
                ips.append(line.strip())

    if (args.ip != None):
        ips.append(args.ip)

    for ip in ips:
        print(ip,":",Ping(ip,args.count, args.timeout))

