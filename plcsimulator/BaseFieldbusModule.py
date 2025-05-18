###############################################################################
# Project: PLC Simulator
# Purpose: Base class to encapsulate default fieldbus module functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

"""
PLC simulator base fieldbus module

This module contains the base class for fieldbus classes.  Fieldbus-specific classes should inherit from this class.
"""

class BaseFieldbusModule(object):
    """
    Base class for fieldbus classes
    """

    def __init__(self, id):
        """
        Constructor

        :param id: The class instance ID
        :type id: str
        """

        self.id = id
        self.conf = {}
        self.memory_manager = None
        self.conn = None

    def get_id(self):
        """
        Get this class instance ID

        :returns: The class instance ID
        """

        return self.id

    def init(self, conf={}, memory_manager=None):
        """
        Initialise the fieldbus-specific PLC class instance

        :param conf: The class configuration section
        :type conf: dict
        :param memory_manager: The instantiated memory_manager object
        :type memory_manager: plcsimulator.MemoryManager.MemoryManager
        """

        self.conf = conf
        self.memory_manager = memory_manager

