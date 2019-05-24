#!/usr/bin/python3
"""
This is ssh wrapper to perform task on multiple servers. Its mainly use to execute command on remote machine and
can't be use for interactive session. The list of the servers need to be provide with options '-f' and execute
commands by using option -C and the commands should be separated by ';'. Also you can execute the script available
on the local machine using -S. This will copy the local script to remote server and execute the script.

This script is capable of multiprocessing and execute the commands simultaneously on multiple servers.
"""
import paramiko
import os
import pingip
import argparse
import multiprocessing as mp
from time import sleep


class Ssh:

    def __init__(self, username="kannan", password=None, pkey=None, timeout=25, server=None,
                 port=22, interactive=False):
        self.user = username
        self.password = password
        self.timeout = 25
        self.connection = False
        self.server = server
        self.error = None
        self.ping = None
        self.sshout = None
        self.ssherr = None
        self.output = {}
        self.execution = True
        self.sftp_connection = None
        self.sftp = None
        self.client = None
        self.command_error = {}
        if self.server is not None:
            self.ping = pingip.Ping(self.server, count=1, timeout=1)

        self.pkey = os.path.expanduser('~/.ssh/id_rsa') if not pkey else pkey
        if self.pkey is not None:
            if os.path.exists(self.pkey):
                self.pkey = paramiko.RSAKey.from_private_key_file(self.pkey)

    def connect(self):
        if self.ping == 'Dead':
            self.error = "not able to ping".format(self.server)
            self.connection = False
            return self.connection
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.pkey is not None:
                self.client.connect(timeout=self.timeout, hostname=self.server, username=self.user, pkey=self.pkey)
            elif self.password is not None:
                self.client.connect(timeout=self.timeout, hostname=self.server, username=self.user,
                                    password=self.password)
            else:
                self.connection = False
                self.error = "No Authentication method defined"
        except Exception as error:
            self.error = error
        else:
            self.connection = True
        return self.connection

    def execute(self, commands=None):
        self.output = {}
        try:
            if not self.connection:
                self.connect()
            if self.connection is False:
                self.execution = False
            for command in commands:
                command_stat = command + ";echo $?"
                stdin, stdout, stderr = self.client.exec_command(command_stat, get_pty=True)
                self.sshout = stdout.read()
                self.ssherr = stderr.read()
                if type(self.sshout) == type(bytes(1)):
                    self.sshout = self.sshout.decode()
                    self.ssherr = self.ssherr.decode()
                output = self.sshout.split('\n')
                self.command_error[command] = int(output[-2])
                self.output[command] = ('\n'.join(output[:-2]), self.ssherr)
                del output
        except Exception as error:
            self.error = error
            self.execution = False
        else:
            self.execution = True
        return self.execution

    def Sftp(self):
        if not self.connection:
            self.connect()
        if not self.connection:
            self.sftp_connection = False
            return False
        try:
            self.sftp = self.client.open_sftp()
        except Exception as error:
            self.error = error
            self.sftp_connection = False
        else:
            self.sftp_connection = False
        return self.sftp

    def close(self):
        try:
            self.client.close()
            self.connection = False
        except Exception as error:
            print("Unable to close the connection\n{}".format(error))


if __name__ == "__main__":
    my_pid = os.getpid()
    parser = argparse.ArgumentParser(description="jp is wrapper for ssh to execute commands on remote server")
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-f', action='store', dest='servers', help='In file which contains list of servers',
                        required=True)
    group.add_argument('-S', action='store', dest='script', help='Execute the local script on remote server')
    group.add_argument('-C', action='store', dest='commands', help='Execute the mentioned commands in the servers')
    parser.add_argument('-B', action='store_true', dest="background", default=False,
                        help="Run the commands in background on servers")
    parser.add_argument('-c', action="store", dest="proc_count", default=5,
                        help="Mention the number of process to create to perform the job")
    parser.add_argument('-o', action="store", dest="output", help="Save output under the directory mentioned")
    args = parser.parse_args()
    infile = args.servers
    script = args.script
    commands = args.commands
    background = args.background
    proc_count = args.proc_count
    output_dir = args.output
    servers = []
    try:
        if os.path.getsize(infile) == 0:
            print("Error: Infile size is 0 Bytes")
            exit(1)
    except Exception as error:
        print("Error: {}".format(error))
        exit(1)
    else:
        with open(infile, 'r') as indata:
            for line in indata:
                line = line.rstrip()
                if len(line) != 0:
                    servers.append(line)
        if not servers:
            print("Error: No servers found on infile {}".format(infile))
            exit(1)
    if script is None and commands is None:
        parser.print_help()
        exit(1)
    elif script is not None:
        isvalid = 0
        if os.path.exists(script):
            with open(script, 'r') as indata:
                for line in indata:
                    line = line.rstrip()
                    if len(line) != 0:
                        isvalid = 1
                        break
            if isvalid != 1:
                print("Error: Script mentioned in the argument is empty")
                exit(1)
            commands = ('sh /tmp/' + os.path.basename(script),)
    elif commands is not None:
        commands = commands.split(';')
    if background is not None:
        with open('jp_script_'+str(my_pid)+'.sh', 'w') as data:
            data.write("#!/bin/bash\n")
            data.write("export PATH=/bin/:/usr/bin:/sbin:/usr/sbin:$PATH\n")
            data.write('at now << EOF\n')
            data.write('echo START AT JOBS > /tmp/jp_script_{}.out\n'.format(my_pid))
            for command in commands:
                data.write(command+' >> /tmp/jp_script_{}.out 2>&1\n'.format(my_pid))
            data.write('echo END AT JOBS >> /tmp/jp_script_{}.out\n'.format(my_pid))
            data.write('EOF')
        script = 'jp_script_{}.sh'.format(my_pid)
        commands = ('sh /tmp/{}'.format(script), )

queue = mp.Queue()
procs = []
limits = mp.cpu_count() - 2


def worker(server, commands):
    output = {}
    ssh = Ssh(server=server)
    ssh.connect()
    output['server'] = '{} {} {}'.format('=' * 20, server, '=' * 20)
    if ssh.connection:
        if script is not None:
            curdir = os.getcwd()
            folder, file = os.path.split(script)

            if not folder:
                folder = curdir

            try:
                os.chdir(folder)
                sftp = ssh.Sftp()
                sftp.chdir('/tmp/')
                sftp.put(script, script)
                ssh.execute('/bin/chmod a+x ' + commands[0])
            except Exception as error:
                output['commands'] = error

        ssh.execute(commands)

        if ssh.execution:
            output['commands'] = ssh.output
            output['errors'] = ssh.command_error
        else:
            output['commands'] = output['errors'] = ssh.error

    else:
        output['commands'] = output['errors'] = ssh.error
    queue.put(output)


while servers:
    if len(mp.active_children()) <= limits:
        server = servers.pop()
        proc = mp.Process(target=worker, args=(server, commands), name=server)
        procs.append(proc)
        proc.start()
        sleep(.1)

while mp.active_children():
    while not queue.empty():
        item = queue.get_nowait()
        print(item['server'])
        if type(item['commands']) == type(str()):
            print(item['commands'])
        else:
            for command in item['commands']:
                prefix = "Error: {}".format(command)
                if item['errors'][command] == 0:
                    prefix = "Output: {}".format(command)
                print("{}\n{}".format(prefix, item['commands'][command][0]))
