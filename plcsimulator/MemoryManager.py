###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the memory manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-11
###############################################################################

class MemoryManager(object):

    DEFAULTS = {
        'memspace': {
            'bits': [],
            'words16': [],
            'words32': [],
            'words64': []
        }
    }

    def __init__(self, blen=0, w16len=0, w32len=0, w64len=0, transforms={}):
        self.memspace = self.DEFAULTS['memspace'].copy()
        self.memspace['bits'] = bytearray(blen)
        self.memspace['words16'] = bytearray(w16len * 2)
        self.memspace['words32'] = bytearray(w32len * 4)
        self.memspace['words64'] = bytearray(w64len * 8)
        self.transforms = transforms

    def init_transforms(self):
        pass

    def get_data(self, section=None, addr=None, n=None):
        data = self.memspace[section][addr:n+1]

        return data

