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

    def process_request(self, request):
        response = FieldbusMessage(2048)

        if request.buf[7] == 0x03:
            base_addr = self.DEFAULTS['functions']['0x03']['base_addr']
            addr = request.make_word(8, 10)
            nwords = request.make_word(10, 12)
        else:
            response.buf[7] |= self.DEFAULTS['exception_flag']

