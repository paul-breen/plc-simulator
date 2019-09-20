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
        'exception_flag': 0x80,
        'exception_codes': {
            'illegal_function': 0x01,
            'illegal_data_address': 0x02,
            'illegal_data_value': 0x03,
            'illegal_response_length': 0x04,
            'acknowledge': 0x05,
            'slave_device_busy': 0x06,
            'negative_acknowledge': 0x07,
            'memory_parity_error': 0x08,
            'mbp_gw_path_unavailable': 0x0a,
            'mbp_gw_device_no_response': 0x0b
        }
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

    def construct_exception_response(self, request, excode):
        response = request
        response.buf[7] |= self.DEFAULTS['exception_flag']
        response.buf[8] = self.DEFAULTS['exception_codes'][excode]

        return response

    def service_read_holding_registers_request(self, request):
        log_prefix = '{}: {}:'.format(self.id, self.DEFAULTS['functions']['0x03']['name'])
        addr = request.make_word(8, 9)
        nwords = request.make_word(10, 11)

        try:
            data = self.memory_manager.get_data(section=self.DEFAULTS['word_mem_section'], addr=addr, nwords=nwords)
            data_nbytes = nwords * self.DEFAULTS['word_nbytes']

            logging.debug('{} addr = {}, nwords = {}, data_nbytes = {}, data = {}'.format(log_prefix, addr, nwords, data_nbytes, data))

            response = FieldbusMessage(9 + data_nbytes)
            response.buf[0:8] = request.buf[0:8]
            response.buf[8] = data_nbytes
            response.buf[9:9+data_nbytes+1] = data
        except IndexError as e:
            # Request exceeds bounds of the memory space.  Inform the client
            logging.error(e)
            response = self.construct_exception_response(request, 'illegal_data_address')

        logging.debug('{} response: {}'.format(log_prefix, response.buf))
        self.conn.sendall(response.buf)

        return response

    def service_preset_multiple_registers_request(self, request):
        log_prefix = '{}: {}:'.format(self.id, self.DEFAULTS['functions']['0x10']['name'])
        addr = request.make_word(8, 9)
        nwords = request.make_word(10, 11)
        data_nbytes = request.buf[12]
        data = request.buf[13:13+data_nbytes+1]

        try:
            self.memory_manager.set_data(section=self.DEFAULTS['word_mem_section'], addr=addr, nwords=nwords, data=data)

            logging.debug('{} addr = {}, nwords = {}, data_nbytes = {}, data = {}'.format(log_prefix, addr, nwords, data_nbytes, data))

            response = FieldbusMessage(12)
            response.buf[0:12] = request.buf[0:12]
        except IndexError as e:
            # Request exceeds bounds of the memory space.  Inform the client
            logging.error(e)
            response = self.construct_exception_response(request, 'illegal_data_address')

        logging.debug('{} response: {}'.format(log_prefix, response.buf))
        self.conn.sendall(response.buf)

        return response

    def service_unknown_request(self, request):
        log_prefix = '{}: {}:'.format(self.id, 'Unknown or unsupported function')
        logging.error('{} function = {:#04x}'.format(log_prefix, request.buf[7]))

        # Unknown or unsupported function.  Inform the client
        response = self.construct_exception_response(request, 'illegal_function')
        self.conn.sendall(response.buf)

        return response

