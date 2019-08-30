###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the fieldbus manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

import logging
import importlib
import threading
import copy

class FieldbusManager(object):
    """
    Instantiates fieldbus-specific modules according to the configuration
    """

    def __init__(self, modules=[], memory_manager=None):
        self.modules = modules
        self.memory_manager = memory_manager
        self.modules_table = {}

    def init_modules(self):
        """
        Initialise the fieldbus-specific modules from the configuration
        """

        # Dynamically load, instantiate and initialise the fieldbus classes
        for item in self.modules:
            logging.info("Initialising module {}".format(item['id']))
            m = importlib.import_module(item['module'])
            c = getattr(m, item['class'])
            o = c(item['id'])
            o.init(conf=item['conf'], memory_manager=self.memory_manager)
            self.modules_table.update({item['port']: o})

    def get_module_by_id(self, id):
        """
        Get the module for the given ID

        :param id: The ID of the module
        :type id: str
        :returns: The module
        :rtype: fieldbus object
        """

        for v in self.modules_table.values():
            if v.get_id() == id:
                return v

        return None

    def get_module_by_port(self, port):
        """
        Get the module for the given port

        :param port: The port that the module is mapped to
        :type port: str
        :returns: The module
        :rtype: fieldbus object
        """

        return self.modules_table[port]

    def create_new_backend(self, current_conn, address):
        """
        Create a new backend to service the incoming client request

        Creates a copy of the required fieldbus module and then this copy
        services the client request directly

        :param current_conn: The client socket
        :type current_conn: socket object
        :param address: The address bound to the client end of the connection
        :type address: address object
        """

        logging.debug("New backend to service client on {}".format(address))

        # Get the listener port and map it to the corresponding fieldbus module
        port = current_conn.getsockname()[1]

        plc = copy.copy(self.get_module_by_port(port))
        plc.conn = current_conn
        plc.process_request()

