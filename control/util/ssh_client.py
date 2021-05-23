import paramiko
import logging

from control.config.communication_config import CommunicationConfig

import socket

from time import sleep

import os


class SSHClient:

    def __init__(self, ip_address):
        ssh_conf = CommunicationConfig()

        self.ip_address = ip_address

        self.key = ssh_conf.key_path + ssh_conf.key_file
        self.user = ssh_conf.user
        self.port = ssh_conf.ssh_port
        self.repeat = ssh_conf.repeat
        self.connection_timeout = ssh_conf.connection_timeout
        self.retry_interval = ssh_conf.retry_interval

        self.client = None
        self.ssh_transp = None
        self.chan = None

    """
    This will check if the connection is still availlable.

    Return (bool) : True if it's still alive, False otherwise.
    """

    @property
    def is_active(self):

        # Check if client was initiated
        if self.client is None:
            return False

        try:
            self.client.exec_command('ls', timeout=30)
            return True
        except Exception as e:
            logging.error("<SSH Client>: Connection lost : " + str(e))
            return False

    '''
    Open a ssh connection
    Return (bool): True if the connection was open, False otherwise
    '''

    def open_connection(self):

        if not self.is_active:

            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            for x in range(self.repeat):

                try:
                    self.client.connect(
                        hostname=self.ip_address,
                        port=self.port,
                        username=self.user,
                        key_filename=self.key,
                        timeout=self.connection_timeout
                    )
                    return True

                except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
                        paramiko.SSHException, socket.error) as e:

                    # logging.info("<SSH Client>:" + str(x) + "> " + str(e))

                    sleep(self.retry_interval)
        else:
            logging.warning("<SSH Client>: Connection was already activated")

        return False

    '''
    close the current ssh connection
    Return (bool):  True if it was closed, False otherwise
    '''

    def close_connection(self):

        try:
            self.client.close()
            return True
        except Exception as e:
            logging.error("<SSH Client>: closing connection error " + str(e))
            return False

    def execute_command(self, command, output=False):
        self.ssh_transp = self.client.get_transport()
        self.chan = self.ssh_transp.open_session()

        self.chan.setblocking(0)

        self.chan.exec_command(command)

        if output:
            sleep(1)
            return self.get_output()

    def put_file(self, source, target, item):

        ftp_client = self.client.open_sftp()

        ftp_client.put(os.path.join(source, item), os.path.join(target, item))

        ftp_client.close()

    def put_dir(self, source, target, ignore_existing=True):
        """
        Uploads the contents of the source directory to the target path. The
        target directory needs to exists. All subdirectories in source are
        created under target.
        """

        ftp_client = self.client.open_sftp()

        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                ftp_client.put(os.path.join(source, item), os.path.join(target, item), confirm=True)
                self.client.exec_command('chmod +x {}'.format(os.path.join(target, item)))

            else:
                try:
                    folder = os.path.join(target, item)
                    ftp_client.mkdir(folder)
                    # self.execute_command("sudo chmod 777 {} ".format(folder))
                except IOError:
                    if ignore_existing:
                        pass
                    else:
                        raise

                self.put_dir(os.path.join(source, item), os.path.join(target, item))

        ftp_client.close()

    def get_output(self):

        outdata = bytes()
        errdata = bytes()

        try:
            while True:
                while self.chan.recv_ready():
                    outdata += self.chan.recv(1000)
                while self.chan.recv_stderr_ready():
                    errdata += self.chan.recv_stderr(1000)
                if self.chan.exit_status_ready():
                    break

            retcode = self.chan.recv_exit_status()
            # self.ssh_transp.close()

            # logging.info("ApplicationConfig on instance {} return code: {} ".format(
            #     self.ip_address,
            #     retcode
            # ))

        except Exception as e:
            logging.error("<SSH Client> Get output error: except")
            logging.error(e)
            raise

        return outdata.decode('utf-8'), errdata.decode('utf-8'), retcode

    @property
    def app_is_running(self):

        try:
            status = not self.chan.exit_status_ready()
        except AttributeError:
            status = False

        # if exit_status is true: app is not running
        return status
