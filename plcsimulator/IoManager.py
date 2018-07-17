###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the IO manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-17
###############################################################################

class IoManager(object):

    DEFAULTS = {
        'byteorder': 'big'
    }

    def __init__(self, conf, memory_manager=None):
        self.conf = conf
        self.memory_manager = memory_manager

    def init_io(self):
        ### TEMP. DURING DEV. ###
        for i in range(0, 100):
            data = i.to_bytes(2, byteorder=self.DEFAULTS['byteorder'])
            self.memory_manager.set_data(section='words16', addr=i, n=2, data=data)

