###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the IO manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-17
###############################################################################

import logging
import threading
import time

class IoManager(object):

    DEFAULTS = {
        'byteorder': 'big'
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
            # Generate an ID for this simulation from its configuration
            mem_id = ':'.join([str(x) for x in conf['memspace'].values()])
            func_id = ':'.join([str(x) for x in conf['function'].values()])
            id = ':'.join([mem_id, func_id])
        except KeyError:
            pass

        return id

    def run_simulation(self, conf):
        sources = {
            'counter': 0,
            'binary': 0
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

        try:
            wlen = self.memory_manager.get_section_word_len(conf['memspace']['section'])
            nwords = int(conf['memspace']['nwords'])

            if conf['function']['type'] == 'counter':
                value = sources['counter']
                sources['counter'] += 1
                b = value.to_bytes(wlen, byteorder=self.DEFAULTS['byteorder'])

                for i in range(nwords):
                    data += b
            elif conf['function']['type'] == 'binary':
                value = sources['binary']
                sources['binary'] = int(not value)
                b = value.to_bytes(wlen, byteorder=self.DEFAULTS['byteorder'])

                for i in range(nwords):
                    data += b

        except KeyError:
            pass

        return data

