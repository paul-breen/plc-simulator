###############################################################################
# Project: PLC Simulator
# Purpose: Base class to encapsulate default fieldbus module functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

class BaseFieldbusModule(object):
    def __init__(self, id):
        self.id = id
        self.conf = {}
        self.memory_manager = None
        self.conn = None

    def get_id(self):
        """
        Get this module's ID

        :returns: The module ID
        """

        return self.id

    def init(self, conf={}, memory_manager=None):
        """
        Initialise the module

        :returns: The module
        """

        self.conf = conf
        self.memory_manager = memory_manager

