###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the IO manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-17
###############################################################################

import logging
import threading
import time
import math

class IoManager(object):

    DEFAULTS = {
        'byteorder': 'big',
        'wave': {
            'types': ['sin','sine','cos','cosine','sawtooth','square'],
            'resolution': 1e3
        }
    }

    def __init__(self, conf, memory_manager=None):
        self.conf = conf
        self.memory_manager = memory_manager

    def init_io(self):
        for conf in self.conf['simulations']:
            id = self.get_simulation_id(conf)
            logging.info('Starting simulation {}'.format(id))

            # N.B.: args expects a tuple, hence the trailing comma.  Setting
            # the thread's daemon status to True, ensures that the thread will
            # terminate when the application main thread is terminated
            simulation = threading.Thread(target=self.run_simulation, args=(conf,))
            simulation.daemon = True
            simulation.start()

    def get_simulation_id(self, conf):
        id = ''

        try:
            id = conf['id']
        except KeyError:
            pass

        if not id:
            # Generate an ID for this simulation from its configuration
            mem_id = ':'.join([str(x) for x in conf['memspace'].values()])
            func_id = ':'.join([str(x) for x in conf['function'].values()])
            id = ':'.join([mem_id, func_id])

        return id

    def run_simulation(self, conf):
        sources = {
            'counter': 0
        }

        while True:
            data = self.simulate_data(conf, sources)
            self.memory_manager.set_data(**conf['memspace'], data=data)

            try:
                time.sleep(conf['pause'])
            except KeyError:
                pass

    def simulate_data(self, conf, sources):
        data = bytearray(0)

        wlen = self.memory_manager.get_section_word_len(conf['memspace']['section'])
        nwords = int(conf['memspace']['nwords'])

        if conf['function']['type'] == 'counter':
            value = sources['counter']
            sources['counter'] = (value + 1) % 2**(wlen * 8)
            data = self.value_to_bytes(value, nwords, wlen)
        elif conf['function']['type'] == 'binary':
            value = sources['counter']
            sources['counter'] = (value + 1) % 2
            data = self.value_to_bytes(value, nwords, wlen)
        elif conf['function']['type'] == 'static':
            value = int(conf['function']['value'])
            data = self.value_to_bytes(value, nwords, wlen)
        elif conf['function']['type'] in self.DEFAULTS['wave']['types']:
            res = int(self.DEFAULTS['wave']['resolution'])
            value = sources['counter']
            sources['counter'] = (value + 1) % (2 * res + 1)

            if conf['function']['type'] in ['sin','sine']:
                y = int(math.sin((value / res) * math.pi) * res + res)
            elif conf['function']['type'] in ['cos','cosine']:
                y = int(math.cos((value / res) * math.pi) * res + res)
            elif conf['function']['type'] == 'sawtooth':
                y = value
            elif conf['function']['type'] == 'square':
                w = math.sin((value / res) * math.pi)
                y = 1 * res if w < 0.0 else 1 * res + res

            data = self.value_to_bytes(y, nwords, wlen)

        return data

    def value_to_bytes(self, value, nwords, wlen):
        data = bytearray(0)
        b = value.to_bytes(wlen, byteorder=self.DEFAULTS['byteorder'])

        for i in range(nwords):
            data += b

        return data

