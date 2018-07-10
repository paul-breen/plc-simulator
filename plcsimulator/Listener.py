###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the listener functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

import logging
import socket
import threading

from plcsimulator.FieldbusManager import FieldbusManager

class Listener(object):
    """
    Main server daemon for the PLC simulator
    """

    DEFAULTS = {
        'conf': {
            'host': 'localhost',
            'port': 5555
        }
    }

    def __init__(self, conf={}):
        self.conf = conf
        self.conn = None
        self.host = self.conf['listener']['host']
        self.port = self.conf['listener']['port']
 
    def configure_socket(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn.bind((self.host, self.port))

    def listen(self, backlog=10):
        self.conn.listen(backlog)

    def service_client_requests(self):
        self.configure_socket()
        backlog = self.conf['listener']['backlog']
        self.listen(backlog=backlog)

        self.fieldbus_manager = FieldbusManager(self.conf)
        self.fieldbus_manager.init_modules()

        logging.info("Listening on {}:{}".format(self.host, self.port))

        while True:
            current_conn, address = self.conn.accept()

            backend = threading.Thread(target=self.fieldbus_manager.create_new_backend, args=(current_conn, address))
            backend.start()

