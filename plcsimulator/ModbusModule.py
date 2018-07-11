###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate Modbus PLC functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

from plcsimulator.BaseFieldbusModule import BaseFieldbusModule
from plcsimulator.FieldbusMessage import FieldbusMessage

class ModbusModule(BaseFieldbusModule):

    DEFAULTS = {
        'blen': 2048,
        'functions': {
            '0x03': {
                'name': 'read_holding_registers',
                'code': 0x03,
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

        response = FieldbusMessage(self.blen)

        if request.buf[7] == 0x03:
            base_addr = self.DEFAULTS['functions']['0x03']['base_addr']
            addr = request.make_word(8, 9)
            nwords = request.make_word(10, 11)

            data = self.memory_manager.get_data(section='words16', addr=addr, n=nwords)
        else:
            response.buf[7] |= self.DEFAULTS['exception_flag']

