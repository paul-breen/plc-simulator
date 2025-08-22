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

import logging
import socket
import select

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

    def service_client(self):
        """
        Service the client

        This is the entry point for a new backend from the FieldbusManager

        * If this Fieldbus module's configuration has `"one_shot": true`,
          then a single request is handled and the connection is closed.
          Otherwise, the connection is kept open and multiple requests are
          serviced until the client closes the connection.
        """

        try:
            if 'one_shot' in self.conf and self.conf['one_shot'] is True:
                retval = self.handle_request()
            else:
                while True:
                    retval = self.handle_request()

                    if retval != 0:
                        break
        except Exception as e:
            logging.debug("Error detected servicing client: {}".format(e))

        # Ensure we close the socket
        logging.debug("Closing backend")
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()

    def handle_request(self, timeout=60):
        """
        Handle an incoming request

        Wait until a client sends a request, then process it

        :param timeout: Timeout for checking for an incoming request
        :type timeout: int
        :returns: Zero to continue to service requests or non-zero if done
        :rtype: int
        """

        retval = 0
        rfds, wfds, efds = select.select([self.conn], [], [], timeout)

        if len(rfds) > 0:
            if self.conn in rfds:
                retval = self.process_request()

        return retval

