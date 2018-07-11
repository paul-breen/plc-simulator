###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate a generic fieldbus message
# Author:  Paul M. Breen
# Date:    2018-07-11
###############################################################################

class FieldbusMessage(object):

    DEFAULTS = {
        'byteorder': 'big'
    }

    def __init__(self, blen):
        self.blen = blen
        self.buf = bytearray(blen)

    def make_word(self, start, end):
        """
        Make a word from the given contiguous byte range from the buffer

        :param start: The start byte offset in the buffer
        :type start: int
        :param end: The end byte offset in the buffer
        :type end: int
        :returns: The (end - start)-byte word
        :rtype int:
        """

        buf_bytes = self.buf[start:end+1]
        word = int.from_bytes(buf_bytes, byteorder=self.DEFAULTS['byteorder'])

        return word

