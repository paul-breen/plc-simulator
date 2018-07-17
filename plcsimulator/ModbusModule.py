###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate Modbus PLC functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

import logging
import socket

from plcsimulator.BaseFieldbusModule import BaseFieldbusModule
from plcsimulator.FieldbusMessage import FieldbusMessage

class ModbusModule(BaseFieldbusModule):

    DEFAULTS = {
        'min_msg_len': 12,
        'word_nbytes': 2,
        'word_mem_section': 'words16',
        'functions': {
            '0x03': {
                'name': 'read holding registers',
                'code': 0x03,
                'base_addr': 40000
            },
            '0x10': {
                'name': 'preset multiple registers',
                'code': 0x10,
                'base_addr': 40000
            }
        },
        'exception_flag': 0x80
    }

    def recv_request_fragment(self, request, nbytes):
        request.recv_fragment(self.conn, nbytes, flags=socket.MSG_WAITALL)

        if len(request.buf) < nbytes:
            raise ValueError('Request length too short (received {} bytes, expected {} bytes)'.format(len(request.buf), nbytes))

        return request

    def get_request(self):
        request = FieldbusMessage(0)

        # Get the minimum message that is common to all Modbus requests
        self.recv_request_fragment(request, self.DEFAULTS['min_msg_len'])

        # For write requests, we also need to read the data payload.  This
        # consists of the data length byte and the data

        if request.buf[7] == self.DEFAULTS['functions']['0x10']['code']:
            nwords = request.make_word(10, 11)
            msg_nbytes = self.DEFAULTS['min_msg_len'] + 1 + nwords * self.DEFAULTS['word_nbytes']
            self.recv_request_fragment(request, msg_nbytes)

        return request

    def process_request(self):
        request = self.get_request()

        if request.buf[7] == self.DEFAULTS['functions']['0x03']['code']:
            self.service_read_holding_registers_request(request)
        elif request.buf[7] == self.DEFAULTS['functions']['0x10']['code']:
            self.service_preset_multiple_registers_request(request)
        else:
            self.service_unknown_request(request)

    def service_read_holding_registers_request(self, request):
        log_prefix = '{}: {}:'.format(self.id, self.DEFAULTS['functions']['0x03']['name'])
        addr = request.make_word(8, 9)
        nwords = request.make_word(10, 11)

        data = self.memory_manager.get_data(section=self.DEFAULTS['word_mem_section'], addr=addr, nwords=nwords)
        data_nbytes = nwords * self.DEFAULTS['word_nbytes']

        logging.debug('{} addr = {}, nwords = {}, data_nbytes = {}, data = {}'.format(log_prefix, addr, nwords, data_nbytes, data))

        response = FieldbusMessage(9 + data_nbytes)

        response.buf[0:8] = request.buf[0:8]
        response.buf[8] = data_nbytes
        response.buf[9:9+data_nbytes+1] = data

        logging.debug('{} response: {}'.format(log_prefix, response.buf))
        self.conn.sendall(response.buf)

        return response

    def service_preset_multiple_registers_request(self, request):
        log_prefix = '{}: {}:'.format(self.id, self.DEFAULTS['functions']['0x10']['name'])
        addr = request.make_word(8, 9)
        nwords = request.make_word(10, 11)
        data_nbytes = request.buf[12]
        data = request.buf[13:13+data_nbytes+1]

        self.memory_manager.set_data(section=self.DEFAULTS['word_mem_section'], addr=addr, nwords=nwords, data=data)

        logging.debug('{} addr = {}, nwords = {}, data_nbytes = {}, data = {}'.format(log_prefix, addr, nwords, data_nbytes, data))

    def service_unknown_request(self, request):
        request.buf[7] |= self.DEFAULTS['exception_flag']
        self.conn.sendall(request.buf)

        return request

