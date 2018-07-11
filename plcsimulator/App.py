###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the main application functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

from plcsimulator.Configurator import Configurator
from plcsimulator.Listener import Listener
from plcsimulator.FieldbusManager import FieldbusManager
from plcsimulator.MemoryManager import MemoryManager

class App(object):
    """
    Main application for the PLC simulator
    """

    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.conf = {}
 
    def init_components(self):
        self.configurator = Configurator(self.conf_file)
        self.conf = self.configurator.get_configuration()
        self.configurator.setup_logging()

        self.memory_manager = MemoryManager(**self.conf['memory_manager']['memspace'], transforms=self.conf['memory_manager']['transforms'])
        self.memory_manager.init_transforms()

        self.fieldbus_manager = FieldbusManager(**self.conf['fieldbus_manager'], memory_manager=self.memory_manager)
        self.fieldbus_manager.init_modules()

        self.listener = Listener(**self.conf['listener'], fieldbus_manager=self.fieldbus_manager)

    def run(self):
        self.init_components()

        try:
            self.listener.service_client_requests()
        except KeyboardInterrupt:
            pass

