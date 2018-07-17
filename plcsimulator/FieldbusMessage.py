###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate a generic fieldbus message
# Author:  Paul M. Breen
# Date:    2018-07-11
###############################################################################

import time
import socket

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

    def reset_buffer(self):
        """
        Reset the buffer
        """

        self.buf = bytearray(self.blen)

    def recv_fragment(self, conn, nbytes, timeout=None, ntries=1, pause=0,
                      flags=0):
        """
        Receive a fragment of an incoming message into the buffer

        Example:

        Say we have a message header of 8 bytes, that contains the length of
        a varying data payload.  The length is in byte 4.  We first read the
        header fragment, calculate the total message size (header + data), and
        then append the data fragment onto the buffer

          msg.recv_fragment(conn, 8)
          msg.recv_fragment(conn, 8 + msg.buf[3])

        :param conn: The socket to receive the message on
        :type conn: socket.socket
        :param nbytes: The total required bytes of the whole message.  The
                       number of bytes to read in this call is calculated as
                       the difference of nbytes and the length of the buffer
                       from any earlier calls to this function
        :type nbytes: int
        :param timeout: The timeout (s) to read data from the socket.  If
                        timeout is 0, then socket is in non-blocking mode,
                        if timeout is None, socket is in blocking mode
        :type timeout: float or None
        :param ntries: The maximum number of tries to read the message fragment
        :type ntries: int
        :param pause: The time to pause (s) between tries
        :type pause: float
        :param flags: Flags bitmask for the recv() call
        :type flags: int
        """

        # Set a timeout to make calls to recv() non-blocking
        if timeout is not None:
            orig_timeout = conn.gettimeout()
            conn.settimeout(timeout)

        for i in range(ntries):
            try:
                nbytes_left = nbytes - len(self.buf)

                if nbytes_left < 1:
                    break

                # Append this message fragment to the total message buffer
                fragment = conn.recv(nbytes_left, flags)
                self.buf += bytearray(fragment)

                if len(self.buf) >= nbytes:
                    break
                elif len(fragment) < 1:
                    break
                else:
                    time.sleep(pause)
            except socket.timeout:
                pass

        if timeout is not None:
            conn.settimeout(orig_timeout)

