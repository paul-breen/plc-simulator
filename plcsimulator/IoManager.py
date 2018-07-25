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
import random

class IoManager(object):

    DEFAULTS = {
        'byteorder': 'big',
        'wave': {
            'types': ['sin','sine','cos','cosine','sawtooth','square'],
            'resolution': 1e3
        },
        'range': {                # N.B.: stop is calculated from word length
            'types': ['counter','randrange'],
            'start': 0,
            'step': 1
        },
        'random': {
            'types': ['randrange','lognormal','uniform'],
            'resolution': 1e3,
            'lognormal': {'mu': 0, 'sigma': 1},
            'uniform': {'a': 0, 'b': 1}
        }
    }

    def __init__(self, conf, memory_manager=None):
        self.conf = conf
        self.memory_manager = memory_manager

    def init_io(self):
        for conf in self.conf['simulations']:
            id = self.define_id(conf)
            logging.info('Starting simulation {}'.format(id))

            # N.B.: args expects a tuple, hence the trailing comma.  Setting
            # the thread's daemon status to True, ensures that the thread will
            # terminate when the application main thread is terminated
            simulation = threading.Thread(target=self.run_simulation, args=(conf,))
            simulation.daemon = True
            simulation.start()

    def define_id(self, conf):
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
            conf['id'] = id

        return id

    def define_range(self, conf):
        range_params = []
        wlen = self.memory_manager.get_section_word_len(conf['memspace']['section'])
        start = self.DEFAULTS['range']['start']
        stop = 2**(wlen * 8)
        step = self.DEFAULTS['range']['step']

        try:
            range_params = conf['function']['range']
        except KeyError:
            pass

        if len(range_params) == 0:
            range_params = [start, stop, step]
        elif len(range_params) == 1:                  # Only stop given
            range_params.append(range_params[0])
            range_params[0] = start
            range_params.append(step)
        elif len(range_params) == 2:
            if range_params[1] < range_params[0]:     # Decrementing range
                range_params.append(-step)
            else:
                range_params.append(step)

        conf['function']['range'] = range_params

        return range_params

    def define_parameter(self, name, conf, default):
        param = default[name]

        try:
            param = conf[name]
        except KeyError:
            pass

        return param

    def run_simulation(self, conf):
        sources = {
            'counter': 0
        }

        self.init_simulation(conf, sources)

        while True:
            data = self.simulate_data(conf, sources)
            self.memory_manager.set_data(**conf['memspace'], data=data)

            try:
                time.sleep(conf['pause'])
            except KeyError:
                pass

    def init_simulation(self, conf, sources):
        # If constrained to a range, ensure the range is fully specified and
        # that the sources are suitably initialised
        if conf['function']['type'] in self.DEFAULTS['range']['types']:
            self.define_range(conf)
            sources['counter'] = conf['function']['range'][0]

        if conf['function']['type'] in self.DEFAULTS['random']['types']:
            try:
                random.seed(a=conf['function']['seed'])
            except KeyError:
                pass

        # Fallback to default parameters if not specified in configuration
        if conf['function']['type'] == 'lognormal':
            conf['function']['mu'] = self.define_parameter('mu', conf['function'], self.DEFAULTS['random']['lognormal'])
            conf['function']['sigma'] = self.define_parameter('sigma', conf['function'], self.DEFAULTS['random']['lognormal'])
        elif conf['function']['type'] == 'uniform':
            conf['function']['a'] = self.define_parameter('a', conf['function'], self.DEFAULTS['random']['uniform'])
            conf['function']['b'] = self.define_parameter('b', conf['function'], self.DEFAULTS['random']['uniform'])

    def simulate_data(self, conf, sources):
        data = bytearray(0)

        wlen = self.memory_manager.get_section_word_len(conf['memspace']['section'])
        nwords = int(conf['memspace']['nwords'])

        if conf['function']['type'] == 'counter':
            value = sources['counter']
            sources['counter'] = self.get_next_range_value(conf['function']['range'], value)
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
                y = res if w < 0.0 else 2 * res

            data = self.value_to_bytes(y, nwords, wlen)
        elif conf['function']['type'] == 'randrange':
            value = random.randrange(*conf['function']['range'])
            data = self.value_to_bytes(value, nwords, wlen)
        elif conf['function']['type'] in self.DEFAULTS['random']['types']:
            res = int(self.DEFAULTS['random']['resolution'])

            if conf['function']['type'] == 'lognormal':
                w = random.lognormvariate(conf['function']['mu'], conf['function']['sigma'])
                y = int(w * res) % 2**(wlen * 8)  # Avoid OverflowError
            elif conf['function']['type'] == 'uniform':
                w = random.uniform(conf['function']['a'], conf['function']['b'])
                y = int(w * res)

            data = self.value_to_bytes(y, nwords, wlen)
        elif conf['function']['type'] == 'copy':
            data = self.memory_manager.get_data(**conf['source']['memspace'])
 
        return data

    def value_to_bytes(self, value, nwords, wlen):
        data = bytearray(0)
        b = value.to_bytes(wlen, byteorder=self.DEFAULTS['byteorder'])

        for i in range(nwords):
            data += b

        return data

    def get_next_range_value(self, range_params, value):
         next_value = value + range_params[2]

         if range_params[2] < 0:
             if next_value <= range_params[1]:
                 next_value = range_params[0]
         else:
             if next_value >= range_params[1]:
                 next_value = range_params[0]

         return next_value

