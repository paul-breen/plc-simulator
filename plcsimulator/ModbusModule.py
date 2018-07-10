###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate Modbus PLC functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

from plcsimulator.BaseFieldbusModule import BaseFieldbusModule

class ModbusModule(BaseFieldbusModule):
    def __init__(self, id):
        super().__init__(id)

