import os
import subprocess


class GfServer:
    def __init__(self, location, servername, serverport):
        self.location = location
        self.servername = servername
        self.serverport = serverport
        self._validate()

    def _validate(self):
        if not os.path.isfile(self.location):
            raise ValueError('gfServer executable could not be found in {}'.format(self.location))
        try:
            self.serverport = int(self.serverport)
        except ValueError:
            raise ValueError('port must be an integer, got {}'.format(self.serverport))

    def test_server(self):
        """
        tests the gfServer and returns True if the server is working

        :param gfserver: str, location of the gfServer executable
        :param servername: str, the name of the gfServer
        :param serverport: int, the port of the gfServer
        :return: bool, True if the server is responding correctly, False, if the server does not responds or the response is incorrect
        """

        command_line = '{} status {} {}'.format(self.gfserver,
                                                self.servername,
                                                self.serverport)

        try:
            gfserver_response = subprocess.check_output([command_line], shell=True, stderr=subprocess.STDOUT)
        except:
            return False

        if gfserver_response.startswith('Couldn'):
            return False
        return 'version' in gfserver_response and 'port' in gfserver_response and 'host' in gfserver_response and 'type' in gfserver_response
