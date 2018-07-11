###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the listener functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

import logging
import socket
import threading

class Listener(object):
    """
    Main server daemon for the PLC simulator
    """

    def __init__(self, host='localhost', port=5555, backlog=10,
                 fieldbus_manager=None):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.fieldbus_manager = fieldbus_manager
        self.conn = None
 
    def configure_socket(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn.bind((self.host, self.port))

    def listen(self, backlog=10):
        self.conn.listen(backlog)

    def service_client_requests(self):
        self.configure_socket()
        self.listen(backlog=self.backlog)

        logging.info("Listening on {}:{}".format(self.host, self.port))

        while True:
            current_conn, address = self.conn.accept()

            backend = threading.Thread(target=self.fieldbus_manager.create_new_backend, args=(current_conn, address))
            backend.start()

