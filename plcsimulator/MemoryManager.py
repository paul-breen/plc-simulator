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

BITS_PER_BYTE = 8

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
        bits_nbytes = blen // BITS_PER_BYTE

        if blen % BITS_PER_BYTE > 0:
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

    def lshift_bits(self, data, n, length=None, truncate=False):
        """
        Left-shift the bits in the given data

        :param data: The data array
        :type data: bytearray
        :param n: The number of bits to left-shift by
        :type n: int
        :param length: The length of the returned data.  Defaults to the
        length of the given data
        :type length: int
        :param truncate: If False, an additional byte is prepended to the
        given data for the bits to be left-shifted into.  If True, the
        left-shifted bits just fall off the end
        :type truncate: bool
        :returns: The left-shifted data
        :rtype: bytearray
        """

        byteorder = self.DEFAULTS['byteorder']

        if not truncate:
            # Add byte to start of data to allow bits to be left-shifted into it
            data.insert(0, 0x00)

        length = length or len(data)
        bits = int.from_bytes(data, byteorder=byteorder)
        bits = bits << n

        return bytearray(bits.to_bytes(length, byteorder=byteorder))

    def rshift_bits(self, data, n, length=None, truncate=False):
        """
        Right-shift the bits in the given data

        :param data: The data array
        :type data: bytearray
        :param n: The number of bits to right-shift by
        :type n: int
        :param length: The length of the returned data.  Defaults to the
        length of the given data
        :type length: int
        :param truncate: If False, an additional byte is appended to the
        given data for the bits to be right-shifted into.  If True, the
        right-shifted bits just fall off the end
        :type truncate: bool
        :returns: The right-shifted data
        :rtype: bytearray
        """

        byteorder = self.DEFAULTS['byteorder']

        if not truncate:
            # Add byte to end of data to allow bits to be right-shifted into it
            data.extend(bytearray(1))

        length = length or len(data)
        bits = int.from_bytes(data, byteorder=byteorder)
        bits = bits >> n

        return bytearray(bits.to_bytes(length, byteorder=byteorder))

    def calc_byte_mask(self, start_bit, end_bit):
        """
        Calculate the bits to mask in a byte for the given bit addresses

        :param start_bit: The start bit address
        :type start_bit: int
        :param end_bit: The end bit address
        :type end_bit: int
        :raises: ValueError if difference of bit addresses > BITS_PER_BYTE
        :returns: The bit mask for the byte covered by the given bit addresses
        :rtype: byte
        """

        if end_bit - start_bit > BITS_PER_BYTE:
            raise ValueError("Invalid total bit length for a byte: {}:{}".format(start_bit, end_bit))

        start_nbits = start_bit % BITS_PER_BYTE
        end_nbits = end_bit % BITS_PER_BYTE

        start_mask = 2**start_nbits - 1
        end_mask = 2**BITS_PER_BYTE - 2**(end_nbits + 1)
        mask = (start_mask & 0xff) + (end_mask & 0xff)
        mask = ~mask & 0xff

        return mask

    def calc_masks(self, addr, nbits):
        """
        Calculate the bit masks for the bytes covered by the given bit range

        The returned bit masks are addressed from right-to-left.
        That is, bit zero refers to the right-most bit in the last byte of
        the bits section memory space

        :param addr: The start address of the bit range
        :type addr: int
        :param nbits: The number of bits in the bit range, inclusive
        :type nbits: int
        :returns: The bit masks for the bytes covered by the given bit range
        :rtype: bytearray
        """

        # For ease of calculation, we first calculate the bitmasks addressing
        # in the left-to-right direction, and then reverse them to the
        # right-to-left direction for use by the caller

        masks = bytearray(0)
        start_addr = addr
        end_addr = addr + nbits
        nbytes = end_addr // BITS_PER_BYTE - start_addr // BITS_PER_BYTE

        if end_addr % BITS_PER_BYTE > 0:
            nbytes += 1

        start_bit = start_addr
        end_bit = (start_bit + BITS_PER_BYTE) // BITS_PER_BYTE * BITS_PER_BYTE - 1

        if end_bit > end_addr - 1:
            end_bit = end_addr - 1

        for i in range(nbytes):
            mask = self.calc_byte_mask(start_bit, end_bit)
            masks.append(mask)
            start_bit = end_bit + 1
            end_bit = start_bit + BITS_PER_BYTE - 1

            if end_bit > end_addr - 1:
                end_bit = end_addr - 1

        masks.reverse()

        return masks

    def calc_mem_slice_byte_bounds(self, addr, nbits, section='bits'):
        """
        Calculate the memory slice byte bounds covered by the given bit range

        As the bit range is addressed from right-to-left, the right_byte is
        set as None if it is the last byte of the bits section memory space.
        This is required so that the slice left_byte:right_byte includes
        the last byte

        :param addr: The start address of the bit range
        :type addr: int
        :param nbits: The number of bits in the bit range, inclusive
        :type nbits: int
        :param section: The memory space section
        :type section: str
        :raises: IndexError if the bounds of the section would be exceeded
        :returns: The left and right byte addresses marking the bounds
        :rtype: tuple of ints (the second of which can be None)
        """

        start_byte = addr // BITS_PER_BYTE
        end_byte = (addr + nbits) // BITS_PER_BYTE
        nbytes = end_byte - start_byte

        self.check_bounds(section=section, addr=start_byte, nwords=nbytes)

        right_byte = (start_byte + 1) * -1
        left_byte = (end_byte + 1) * -1

        if (addr + nbits) % BITS_PER_BYTE > 0:
            right_byte += 1
        if (addr + nbits) % BITS_PER_BYTE == 0:
            left_byte += 1
            right_byte += 1
        if right_byte == 0:
            right_byte = None

        return left_byte, right_byte

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

    def get_bits(self, section='bits', addr=None, nbits=None):
        """
        Get an arbitrary range of bits from the bits memory space section

        Note that the bit range is ordered from right-to-left

        :param section: The memory space section
        :type section: str
        :param addr: The start bit address in the bits memory space section
        :type addr: int
        :param nbits: The number of bits to get offset from start address
        :type nbits: int
        :returns: The bits
        :rtype: bytearray
        """

        byteorder = self.DEFAULTS['byteorder']

        right_addr = (len(self.memspace[section]) * BITS_PER_BYTE - addr - 1)
        left_addr = right_addr - nbits + 1

        masks = self.calc_masks(addr, nbits)
        left_byte, right_byte = self.calc_mem_slice_byte_bounds(addr, nbits)

        with self.lock:
            mem_slice = self.memspace[section][left_byte:right_byte]

        data = mem_slice.copy()
        data_bits = int.from_bytes(data, byteorder=byteorder)
        masks_bits = int.from_bytes(masks, byteorder=byteorder)

        masked_bits = data_bits & masks_bits
        data = bytearray(masked_bits.to_bytes(len(masks), byteorder=byteorder))
        data = self.rshift_bits(data, addr % BITS_PER_BYTE, truncate=True)

        data_len = nbits // BITS_PER_BYTE

        if nbits % BITS_PER_BYTE > 0:
            data_len += 1

        data = data[(data_len * -1):]

        return data

    def set_bits(self, section='bits', addr=None, nbits=None, data=None):
        """
        Set an arbitrary range of bits in the bits memory space section

        Note that the bit range is ordered from right-to-left

        :param section: The memory space section
        :type section: str
        :param addr: The start bit address in the bits memory space section
        :type addr: int
        :param nbits: The number of bits to set offset from start address
        :type nbits: int
        :param data: The bit values to set in the bits memory space section
        :type data: bytearray
        :returns: The bits
        :rtype: bytearray
        """

        byteorder = self.DEFAULTS['byteorder']

        right_addr = (len(self.memspace[section]) * BITS_PER_BYTE - addr - 1)
        left_addr = right_addr - nbits + 1

        masks = self.calc_masks(addr, nbits)
        left_byte, right_byte = self.calc_mem_slice_byte_bounds(addr, nbits)

        with self.lock:
            mem_slice = self.memspace[section][left_byte:right_byte]

            data = self.lshift_bits(data, addr % BITS_PER_BYTE)

            mem_slice_bits = int.from_bytes(mem_slice, byteorder=byteorder)
            data_bits = int.from_bytes(data, byteorder=byteorder)
            masks_bits = int.from_bytes(masks, byteorder=byteorder)

            patched_bits = data_bits & masks_bits
            patched_bits = patched_bits | (mem_slice_bits & ~masks_bits)
            patched_bytes = bytearray(patched_bits.to_bytes(len(masks), byteorder=byteorder))

            self.memspace[section][left_byte:right_byte] = patched_bytes

        return data

