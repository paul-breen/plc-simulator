###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the listener functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

"""
PLC simulator network listener module

This module contains the listener class.  It manages:

* Creating and binding the TCP listening socket specified in the configuration.
* Listening on the socket for incoming connection requests.
* Creating a backend to service the incoming request.
"""

import logging
import socket
import threading

class Listener(object):
    """
    Main server daemon for the PLC simulator
    """

    def __init__(self, host='localhost', port=5555, backlog=10, fieldbus_manager=None):
        """
        Constructor

        :param host: The host name or address to bind the listening socket to
        :type host: str
        :param port:  The TCP port to bind the listening socket to
        :type port: int
        :param backlog: The number of pending connection requests to handle
        :type backlog: int
        :param fieldbus_manager: The instantiated fieldbus_manager object
        :type fieldbus_manager: plcsimulator.FieldbusManager.FieldbusManager
        """

        self.host = host
        self.port = port
        self.backlog = backlog
        self.fieldbus_manager = fieldbus_manager
        self.conn = None
 
    def configure_socket(self):
        """
        Configure the listening socket
        """

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn.bind((self.host, self.port))

    def listen(self, backlog=10):
        """
        Listen for incoming connection requests

        :param backlog: The number of pending connection requests to handle
        :type backlog: int
        """

        self.conn.listen(backlog)

    def service_client_requests(self):
        """
        Handle incoming connection requests from clients

        * Configure the listening socket.
        * Listen on the socket for incoming connection requests.
        * Pass the connection to a new fieldbus-specific backend to process.
        """

        self.configure_socket()
        self.listen(backlog=self.backlog)

        logging.info("Listening on {}:{}".format(self.host, self.port))

        while True:
            current_conn, address = self.conn.accept()

            backend = threading.Thread(target=self.fieldbus_manager.create_new_backend, args=(current_conn, address))
            backend.start()

