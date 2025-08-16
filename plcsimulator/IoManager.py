###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the IO manager functionality
# Author:  Paul M. Breen
# Date:    2018-07-17
###############################################################################

"""
PLC simulator IO manager module

This module contains the IO manager class.  It manages:

* Initialising each IO simulation specified in the configuration.
* Running each IO simulation according to its parameters.
"""

import logging
import threading
import time
import math
import random

BITS_PER_BYTE = 8

class IoManager(object):
    """
    IO manager for the PLC simulator
    """

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
        """
        Constructor

        :param conf: The IO manager configuration section
        :type conf: dict
        :param memory_manager: The instantiated memory_manager object
        :type memory_manager: plcsimulator.MemoryManager.MemoryManager
        """

        self.conf = conf
        self.memory_manager = memory_manager

    def init_io(self):
        """
        Initialise the IO simulations from the configuration
        """

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
        """
        Get the ID for the simulation or construct one if not present

        If the simulation configuration doesn't include an 'id' key, we
        construct a unique ID from the simulation's memory space and function.

        :param conf: The IO manager configuration section
        :type conf: dict
        :returns: The simulation ID
        :rtype: str
        """

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
        """
        Construct the fully-specified range parameters for the simulation

        The range will contain a start, step, and stop parameter.

        :param conf: The IO manager configuration section
        :type conf: dict
        :returns: The simulation range parameters
        :rtype: list
        """

        range_params = []
        wlen = self.memory_manager.get_section_word_len(conf['memspace']['section'])
        start = self.DEFAULTS['range']['start']
        stop = 2**(wlen * BITS_PER_BYTE)
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
        """
        Get a parameter of the simulation function or a default if not present

        :param name: The parameter name
        :type name: str
        :param conf: The function configuration
        :type conf: dict
        :param default: The parameter default
        :type default: str
        :returns: The simulation function parameter value
        :rtype: number
        """

        param = default[name]

        try:
            param = conf[name]
        except KeyError:
            pass

        return param

    def get_memspace(self, conf):
        """
        Get data from the memory space defined in the given conf

        :param conf: The simulation's memspace configuration
        :type conf: dict
        :returns: The memory space data
        :rtype: bytearray
        """

        if conf['section'] == 'bits':
            data = self.memory_manager.get_bits(**conf)
        else:
            data = self.memory_manager.get_data(**conf)

        return data

    def set_memspace(self, conf, data):
        """
        Set the given data in the memory space defined in the given conf

        :param conf: The simulation's memspace configuration
        :type conf: dict
        :param data: The data to be written to the memory space
        :type data: bytearray
        """

        if conf['section'] == 'bits':
            self.memory_manager.set_bits(**conf, data=data)
        else:
            self.memory_manager.set_data(**conf, data=data)

    def get_memspace_conf_nrefs(self, conf):
        """
        Get the number of references from the given memory space conf

        This can be words or bits depending on the memory space section.
        The more general `refs` can be used for any memory space section type

        :param conf: The simulation's memspace configuration
        :type conf: dict
        :returns: The number of refs (words, bits or refs) from the conf
        :rtype: int
        """

        nrefs = 0

        if 'nwords' in conf:
            nrefs = int(conf['nwords'])
        elif 'nbits' in conf:
            nrefs = int(conf['nbits'])
        elif 'nrefs' in conf:
            nrefs = int(conf['nrefs'])
        else:
            raise ValueError("Unknown memspace ref type: {}".format(conf))

        return nrefs

    def run_simulation(self, conf):
        """
        Run the simulation according to its configuration

        This is the entry point for this simulation's thread

        :param conf: The simulation configuration
        :type conf: dict
        """

        sources = {
            'counter': 0
        }

        self.init_simulation(conf, sources)

        while True:
            data = self.simulate_data(conf, sources)

            if data is not None:
                self.set_memspace(conf['memspace'], data)

            try:
                time.sleep(conf['pause'])
            except KeyError:
                pass

    def init_simulation(self, conf, sources):
        """
        Initialise the simulation according to its configuration

        :param conf: The simulation configuration
        :type conf: dict
        :param sources: Seeds for the simulation values
        :type sources: dict
        """

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
        """
        Generate data for the simulation according to its configuration

        :param conf: The simulation configuration
        :type conf: dict
        :param sources: The simulation value sources (counters)
        :type sources: dict
        :returns: The simulation data values or None if the simulation didn't
        generate any data
        :rtype: bytearray or None
        """

        data = bytearray(0)

        wlen = self.memory_manager.get_section_word_len(conf['memspace']['section'])
        nrefs = self.get_memspace_conf_nrefs(conf['memspace'])

        if conf['function']['type'] == 'counter':
            value = sources['counter']
            sources['counter'] = self.get_next_range_value(conf['function']['range'], value)
            data = self.value_to_bytes(value, nrefs, wlen)
        elif conf['function']['type'] == 'binary':
            value = sources['counter']
            sources['counter'] = (value + 1) % 2
            data = self.value_to_bytes(value, nrefs, wlen)
        elif conf['function']['type'] == 'static':
            value = int(conf['function']['value'])
            data = self.value_to_bytes(value, nrefs, wlen)
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

            data = self.value_to_bytes(y, nrefs, wlen)
        elif conf['function']['type'] == 'randrange':
            value = random.randrange(*conf['function']['range'])
            data = self.value_to_bytes(value, nrefs, wlen)
        elif conf['function']['type'] in self.DEFAULTS['random']['types']:
            res = int(self.DEFAULTS['random']['resolution'])

            if conf['function']['type'] == 'lognormal':
                w = random.lognormvariate(conf['function']['mu'], conf['function']['sigma'])
                y = int(w * res) % 2**(wlen * BITS_PER_BYTE)    # Avoid OverflowError
            elif conf['function']['type'] == 'uniform':
                w = random.uniform(conf['function']['a'], conf['function']['b'])
                y = int(w * res)

            data = self.value_to_bytes(y, nrefs, wlen)
        elif conf['function']['type'] == 'copy':
            data = self.get_memspace(conf['source']['memspace'])
        elif conf['function']['type'] == 'transform':
            buf = self.get_memspace(conf['source']['memspace'])
            word = int.from_bytes(buf, byteorder=self.DEFAULTS['byteorder'])
            value = self.transform_item(word, conf['function']['transform'])

            if value is not None:
                data = self.value_to_bytes(value, nrefs, wlen)
            else:
                data = None
 
        return data

    def value_to_bytes(self, value, nwords, wlen):
        """
        Convert the simulated data value to bytes

        :param value: The simulation data value
        :type value: number
        :param nwords: The number of words that the value should fill
        :type nwords: int
        :param wlen: The length in bytes of a word
        :type wlen: int
        :returns: The simulation data value as bytes
        :rtype: bytearray
        """

        data = bytearray(0)
        b = value.to_bytes(wlen, byteorder=self.DEFAULTS['byteorder'])

        for i in range(nwords):
            data += b

        return data

    def get_next_range_value(self, range_params, value):
        """
        Get the next range value from the given range parameters

        :param range_params: The simulation range parameters
        :type range_params: list
        :param value: The current value from the range
        :type value: number
        :returns: The next value in the range
        :rtype: number
        """

        next_value = value + range_params[2]

        if range_params[2] < 0:
            if next_value <= range_params[1]:
                next_value = range_params[0]
        else:
            if next_value >= range_params[1]:
                next_value = range_params[0]

        return next_value

    def transform_item(self, state, transform):
        """
        Transform the state according to the given transform rules

        The state is the current value of the simulation as a word of the
        simulation's memory space.  This word provides input to the rules
        specified in transform.  The word is transformed according to the
        rules and thereby provides the simulation's data value.

        If the transform output is configured as 'null', then the returned
        data value is simply the value of the state variable.  This is a
        simple passthrough rule.

        :param state: The current state of the simulation as a word value
        :type state: number
        :param transform: The simulation transform rules
        :type transform: dict
        :returns: The input state transformed to the output state
        :rtype: number
        """

        item = None
        t_in = transform['in']
        t_out = transform['out']

        # If the transform output is configured as 'null', then it takes the
        # value of the state variable
        if t_out is None:
            t_out = state

        if isinstance(t_in, (list, tuple)):
            if t_in[0] <= state <= t_in[1]:
                item = t_out
        elif state == t_in:
                item = t_out

        return item

