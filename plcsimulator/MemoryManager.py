###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the memory manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-11
###############################################################################

from threading import Lock

class MemoryManager(object):

    DEFAULTS = {
        'byteorder': 'big',
        'memspace': {
            'bits': [],
            'words16': [],
            'words32': [],
            'words64': []
        }
    }

    def __init__(self, blen=0, w16len=0, w32len=0, w64len=0, transforms={}):
        self.lock = Lock()
        self.memspace = self.DEFAULTS['memspace'].copy()
        self.memspace['bits'] = bytearray(blen)
        self.memspace['words16'] = bytearray(w16len * 2)
        self.memspace['words32'] = bytearray(w32len * 4)
        self.memspace['words64'] = bytearray(w64len * 8)
        self.transforms = transforms

    def init_transforms(self):
        ### TEMP. DURING DEV. ###
        for i in range(0, 100):
            data = i.to_bytes(2, byteorder=self.DEFAULTS['byteorder'])
            self.set_data(section='words16', addr=i, n=2, data=data)

    def get_section_word_len(self, section):
        if section == 'bits':
            word_len = 1
        elif section == 'words16':
            word_len = 2
        elif section == 'words32':
            word_len = 4
        elif section == 'words64':
            word_len = 8
        else:
            raise ValueError("Unknown memspace section: {}".format(section))

        return word_len

    def get_data(self, section=None, addr=None, n=None):
        wlen = self.get_section_word_len(section)

        with self.lock:
            data = self.memspace[section][addr*wlen:addr*wlen+n*wlen]

        return data

    def set_data(self, section=None, addr=None, n=None, data=None):
        wlen = self.get_section_word_len(section)

        with self.lock:
            self.memspace[section][addr*wlen:addr*wlen+n*wlen] = data

        return data

