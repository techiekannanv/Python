from __future__ import print_function
import paramiko
import os.path


class Ssh:

    def __init__(self, username='kannan', password=None, server='localhost', pkey=None):
        self.user = username
        self.passwd = password
        self.server = server
        self.connection = False
        self.pkey = None

        if pkey != None:
            # print("Debug:",pkey)
            if os.path.exists(pkey):
                self.pkey = paramiko.RSAKey.from_private_key_file(pkey)
            else:
                self.pkey = None

    def connect(self):
        self.connection = True

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.passwd == None:
                # print("Debug:",self.pkey)
                self.client.connect(hostname=self.server, username=self.user, pkey=self.pkey)
                print("DEBUG: connected to server {} using ssh key".format(self.server))
            else:
                self.client.connect(hostname=self.server, username=self.user, password=self.passwd)
                print("DEBUG: Connected to server {} using password".format(self.server))
        except Exception as error:
            print("Unable to connect to server {}".format(self.server))
            print("Error: {}".format(error))
            self.connection = False
        # return self.connection

    def execute(self, commands):
        self.execution = True
        self.ssh_out = None
        try:
            if not self.connection:
                self.connect()
            # print("Hello",self.connection)
            if self.connection == False:
                self.execution = False
                return
            counter = 0
            for command in commands:
                counter += 1
                print("Executing command:{} ---> {}".format(counter, command))
                stdin, stdout, stderr = self.client.exec_command(command)
                self.ssh_out = stdout.read()
                self.ssh_error = stderr.read()
                if self.ssh_error:
                    print("Problem occurred while running command {} and the error is\n {}".format(command, self.ssh_error))
                else:
                    if type(self.ssh_out) == type(bytes(1)):
                        self.ssh_out = self.ssh_out.decode()
                    print(self.ssh_out)
        except Exception as error:
            print("Failed to execute commands due to below error\n{}".format(error))
            self.execution = False


    def Sftp(self):
        if self.connection == False:
            self.connect()
        if self.connection == False:
            self.sftp_connection = False
            return False
        self.sftp = self.client.open_sftp()
        return self.sftp

    def close(self):
        try:
            self.client.close()
            self.connection = False
        except Exception as error:
            print("Unable to close the connection\n{}".format(error))


if __name__ == "__main__":
    session = Ssh(pkey='/home/kannan/id_rsa', username='kannan')
    # session = Ssh()
    sftp = session.Sftp()
    sftp.put('ssh.log', 'ssh.log')
    sftp.get('id_rsa.ppk','id_rsa')
    session.execute(('uptime','uname -a', 'cal','echo $HOME', 'echo $USER'))
    session.close()
    
