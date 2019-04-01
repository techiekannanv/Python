import sgc
import multiprocessing as mp
# import json
import argparse
import os
import re



#Process argument passed to the script
parser = argparse.ArgumentParser(description='Execute commands parallel on remote servers')
parser.add_argument('-f', action='store', required=True, dest='file', help='servers list')
group = parser.add_mutually_exclusive_group()
group.add_argument('-c', action='store', dest='commands', help='commands need to execute')
group.add_argument('-S', action='store', dest='script', help='local script which need to execute on remote servers')

options = parser.parse_args()

#Exit if input file is zero
if os.path.getsize(options.file) == 0:
    print("Error: server list file is empty")
    exit(2)

#Process the input file and store the server in list variable servers
file = open(options.file, 'r')
servers = []
for line in file:
    line = line.strip('\n')
    if len(line) == 0 or line in servers:
        continue
    servers.append(line)

#Exit the script if the servers list is empty
if not servers:
    print("Error: server list file is empty")
    exit(2)

#Process the commands passed into the script
commands = []

if options.commands and re.match(r'[a-zA-Z0-9]', options.commands):
    for item in options.commands.split(','):
        item = item.replace('"', '')
        commands.append(item)
    #Exit the script if command list is empty
    if not commands:
        print("Error: command list is empty")
        parser.print_help()
        exit(2)

if options.script:
    commands = ['/tmp/'+os.path.basename(options.script)]

#servers = ['localhost', 'centos6web', 'fedora.kannan.lab', '127.0.0.1', '127.0.0.2',  '127.0.0.3', '127.0.0.4',
#           '127.0.0.100', '127.0.0.200', '127.0.0.150', '127.0.0.10', '127.0.0.20', '127.0.0.30']
# servers = ['centos6web', 'fedora.kannan.lab']
# commands = ('sudo shutdown -h 0',)
# commands = ('uptime', 'uname -a', 'sudo fdisk -l')
queue = mp.Queue()
def worker(server, commands):
    # print(mp.current_process().name)
    output = {}
    output['server'] = server
    session = sgc.Ssh(server=server)

    #     print("Connected to server {}".format(server))
    # else:
    #     print("Unable to connect to server {}\n{}".format(server, session.connection_error))
    if session.ping == 'Alive':
        session.connect()
        # print(session.connection)
        if session.connection == False:
            output['commands'] = session.connection_error
        else:
            if options.script:
                if not os.path.exists(options.script):
                    output['commands'] = "Error: the script location {} not exists".format(options.script)
                    print("Error: the script location {} not exists".format(options.script))
                else:
                    curdir = os.getcwd()
                    folder, file = os.path.split(options.script)
                    if not folder:
                        folder = curdir
                    try:
                        os.chdir(folder)
                        sftp = session.Sftp()
                        sftp.chdir('/tmp')
                        sftp.put(file, file)
                        commands = ('/tmp/'+file,)
                        session.execute(('/bin/chmod a+x /tmp/'+file, ))
                    except Exception as error:
                        output['commands'] = error
            output['commands'] = session.execute(commands)
    else:
        output['commands'] = 'Down'

    queue.put(output)
    # if output != None:
    #     print("Server {}".format(server))
    #     for key in output:
    #         print(key, output[key])

# pool = mp.Pool(processes=mp.cpu_count())
# result = pool.map_async(worker, servers)
# for item in result.get():
#     print(json.dumps(item, indent=4))
procs = []
limits = mp.cpu_count()
while servers:
    if len(mp.active_children()) < limits:
        server = servers.pop()
        proc = mp.Process(target=worker, args=(server, commands), name=server)
        procs.append(proc)
        proc.start()
while mp.active_children() :
    if not queue.empty():
        item = queue.get()

        if item['commands'] == 'Down':
            print("Server: {} : Unable to ping".format(item['server']))
            continue
        if type(item['commands']) != type(dict()):
            print("Server: {} : {}".format(item['server'], item['commands']))
            continue

        print("Server: {}".format(item['server']))
        for command in commands:
            if item['commands'][command][0] != "":
                if options.script:
                    print("Output of Command: {}".format(options.script))
                else:
                    print("Output of Command: {}".format(command))
                print(item['commands'][command][0])
            if item['commands'][command][1] != "":
                print("Error occurred on command: {}".format(command))
                print(item['commands'][command][1])
        print("**************************************************************************")
