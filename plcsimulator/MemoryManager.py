###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the memory manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-11
###############################################################################

"""
PLC simulator memory manager module

This module contains the memory manager class.  It manages:

* Initialising each memory space section specified in the configuration.
* Getting and setting values in a given memory space section.
"""

from threading import Lock

class MemoryManager(object):
    """
    Memory manager for the PLC simulator
    """

    DEFAULTS = {
        'byteorder': 'big',
        'memspace': {
            'bits': [],
            'words16': [],
            'words32': [],
            'words64': []
        }
    }

    def __init__(self, blen=0, w16len=0, w32len=0, w64len=0):
        """
        Constructor

        Note that blen should be a multiple of bits per byte, and if not,
        blen is rounded up accordingly

        :param blen: The number of slots in the bits section
        :type blen: int
        :param w16len: The number of slots in the 16-bit words section
        :type w16len: int
        :param w32len: The number of slots in the 32-bit words section
        :type w32len: int
        :param w64len: The number of slots in the 64-bit words section
        :type w64len: int
        """

        self.lock = Lock()
        self.memspace = self.DEFAULTS['memspace'].copy()

        # Ensure number of bits are aligned to whole byte lengths
        bits_nbytes = blen // 8

        if blen % 8 > 0:
            bits_nbytes += 1

        self.memspace['bits'] = bytearray(bits_nbytes)
        self.memspace['words16'] = bytearray(w16len * 2)
        self.memspace['words32'] = bytearray(w32len * 4)
        self.memspace['words64'] = bytearray(w64len * 8)

    def get_section_word_len(self, section):
        """
        Get the word length of the given memory space section

        :param section: The memory space section
        :type section: str
        :returns: The length of a word in the given section
        :rtype: int
        """
 
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

    def check_bounds(self, section=None, addr=None, nwords=None):
        """
        Do a bounds check on a request to access a given memory space section

        :param section: The memory space section
        :type section: str
        :param addr: The start address in the memory space section
        :type addr: int
        :param nwords: The number of words to access offset from start address
        :type nwords: int
        :raises: IndexError if the bounds of the section would be exceeded
        """
 
        wlen = self.get_section_word_len(section)
        start_addr = addr*wlen
        end_addr = addr*wlen+nwords*wlen

        # Slice doesn't include its end so end_addr can be length of memspace
        if start_addr < 0 or end_addr > len(self.memspace[section]):
            raise IndexError("Memspace section {} bounds exceeded: {}:{}".format(section, start_addr, end_addr))

    def get_data(self, section=None, addr=None, nwords=None):
        """
        Get a slice of data from the given memory space section

        :param section: The memory space section
        :type section: str
        :param addr: The start address in the memory space section
        :type addr: int
        :param nwords: The number of words to get offset from start address
        :type nwords: int
        :returns: The data slice
        :rtype: bytearray
        """

        wlen = self.get_section_word_len(section)

        self.check_bounds(section=section, addr=addr, nwords=nwords)

        with self.lock:
            data = self.memspace[section][addr*wlen:addr*wlen+nwords*wlen]

        return data

    def set_data(self, section=None, addr=None, nwords=None, data=None):
        """
        Set a slice of data in the given memory space section

        :param section: The memory space section
        :type section: str
        :param addr: The start address in the memory space section
        :type addr: int
        :param nwords: The number of words to set offset from start address
        :type nwords: int
        :param data: The data values to set in the memory space section
        :type data: bytearray
        :returns: The data slice
        :rtype: bytearray
        """

        wlen = self.get_section_word_len(section)

        self.check_bounds(section=section, addr=addr, nwords=nwords)

        with self.lock:
            self.memspace[section][addr*wlen:addr*wlen+nwords*wlen] = data

        return data

