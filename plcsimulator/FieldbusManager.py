###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the fieldbus manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

import logging
import importlib
import threading

class FieldbusManager(object):
    """
    Instantiates fieldbus-specific modules according to the configuration
    """

    def __init__(self, modules=[]):
        self.modules = modules
        self.modules_table = {}

    def init_modules(self):
        """
        Initialise the fieldbus-specific modules from the configuration
        """

        # Dynamically load, instantiate and initialise the fieldbus classes
        for item in self.modules:
            logging.info("Initialising module: {}".format(item['id']))
            m = importlib.import_module(item['module'])
            c = getattr(m, item['class'])
            o = c(item['id'])
            o.init(conf=item['conf'])
            self.modules_table.update({o.get_id(): o})

    def get_module(self, id):
        """
        Get the module for the given ID

        :param id: The ID of the module
        :type id: str
        :returns: The module
        :rtype: fieldbus object
        """

        return self.modules_table[id]

    def create_new_backend(self, current_conn, address):
        logging.info("New backend to service client on {}".format(address))

        data = None

        while True:
            data = current_conn.recv(2048)
            data = data.rstrip()

            if data == 'quit':
                current_conn.shutdown(1)
                current_conn.close()
                break
            elif data == 'stop':
                current_conn.shutdown(1)
                current_conn.close()
                exit()
            elif data:
                current_conn.send(data)
                name = threading.current_thread().name
                print('{}: {}'.format(name, data))
            elif not data:
                break

