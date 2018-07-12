###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate Modbus PLC functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

import logging

from plcsimulator.BaseFieldbusModule import BaseFieldbusModule
from plcsimulator.FieldbusMessage import FieldbusMessage

class ModbusModule(BaseFieldbusModule):

    DEFAULTS = {
        'blen': 520,
        'word_nbytes': 2,
        'word_mem_section': 'words16',
        'functions': {
            '0x03': {
                'name': 'read_holding_registers',
                'code': 0x03,
                'base_addr': 40000
            },
            '0x10': {
                'name': 'preset_multiple_registers',
                'code': 0x10,
                'base_addr': 40000
            }
        },
        'exception_flag': 0x80
    }

    def __init__(self, id):
        super().__init__(id)
        self.blen = self.DEFAULTS['blen']

    def process_request(self):
        request = FieldbusMessage(self.blen)
        request.buf = self.conn.recv(self.blen)

        if request.buf[7] == self.DEFAULTS['functions']['0x03']['code']:
            self.service_read_holding_registers_request(request)
        elif request.buf[7] == self.DEFAULTS['functions']['0x10']['code']:
            self.service_preset_multiple_registers_request(request)
        else:
            self.service_unknown_request(request)

    def service_read_holding_registers_request(self, request):
        base_addr = self.DEFAULTS['functions']['0x03']['base_addr']
        addr = request.make_word(8, 9)
        nwords = request.make_word(10, 11)

        data = self.memory_manager.get_data(section=self.DEFAULTS['word_mem_section'], addr=addr, n=nwords)
        data_nbytes = nwords * self.DEFAULTS['word_nbytes']

        logging.debug("Read holding registers: addr = {}, nwords = {}, data_nbytes = {}, data = {}".format(addr, nwords, data_nbytes, data))

        response = FieldbusMessage(9 + data_nbytes)

        response.buf[0:8] = request.buf[0:8]
        response.buf[8] = data_nbytes
        response.buf[9:9+data_nbytes+1] = data

        logging.debug("Read holding registers: response: {}".format(response.buf))
        self.conn.sendall(response.buf)

        return response

    def service_preset_multiple_registers_request(self, request):
        base_addr = self.DEFAULTS['functions']['0x10']['base_addr']
        addr = request.make_word(8, 9)
        nwords = request.make_word(10, 11)
        data_nbytes = request.buf[12]
        data = request.buf[13:13+data_nbytes+1]

        self.memory_manager.set_data(section=self.DEFAULTS['word_mem_section'], addr=addr, n=nwords, data=data)

        logging.debug("Preset multiple registers: addr = {}, nwords = {}, data_nbytes = {}, data = {}".format(addr, nwords, data_nbytes, data))

    def service_unknown_request(self, request):
        request.buf[7] |= self.DEFAULTS['exception_flag']
        self.conn.sendall(request.buf)

        return request

