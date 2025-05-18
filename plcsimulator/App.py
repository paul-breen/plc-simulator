###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the main application functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

"""
PLC simulator main application module

This module contains the main application class for instantiating and running the PLC simulator, including:

* Reading the given simulation configuration file and setting up logging.
* Instantiating the memory manager to provide the memory space of the PLC.
* Instantiating the IO manager to provide the simulated IO of the PLC.
* Instantiating the fieldbus manager to provide a fieldbus-specific interface to the PLC.
* Instantiating the TCP/IP Listener to handle incoming connections.
"""

from plcsimulator.Configurator import Configurator
from plcsimulator.Listener import Listener
from plcsimulator.FieldbusManager import FieldbusManager
from plcsimulator.MemoryManager import MemoryManager
from plcsimulator.IoManager import IoManager

class App(object):
    """
    Main application for the PLC simulator
    """

    def __init__(self, conf_file):
        """
        Constructor

        :param conf_file: Path to the configuration file
        :type conf_file: str
        """

        self.conf_file = conf_file
        self.conf = {}
 
    def init_components(self):
        """
        Instantiate and initialise the main application components
        """

        self.configurator = Configurator(self.conf_file)
        self.conf = self.configurator.get_configuration()
        self.configurator.setup_logging()

        self.memory_manager = MemoryManager(**self.conf['memory_manager']['memspace'])

        self.io_manager = IoManager(self.conf['io_manager'], memory_manager=self.memory_manager)
        self.io_manager.init_io()

        self.fieldbus_manager = FieldbusManager(**self.conf['fieldbus_manager'], memory_manager=self.memory_manager)
        self.fieldbus_manager.init_modules()

        self.listener = Listener(**self.conf['listener'], fieldbus_manager=self.fieldbus_manager)

    def run(self):
        """
        Run the main application

        * Instantiate and initialise the main application components
        * Start the TCP/IP listener to accept incoming client connections
        """

        self.init_components()

        try:
            self.listener.service_client_requests()
        except KeyboardInterrupt:
            pass

