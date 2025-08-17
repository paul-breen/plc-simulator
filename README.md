# PLC Simulator

This project provides an extensible PLC simulation environment.  The MemoryManager provides a configurable linear memory space that is independent of any particular model of PLC.  The IoManager supports a number of simulation functions that can be specified to update memory locations in the MemoryManager's memory space.  The FieldbusManager instantiates configured fieldbus-specific objects that simulate the request/response protocols of PLCs.  The fieldbus-specific object to handle incoming requests is mapped by TCP listening port.  The Listener provides a TCP/IP interface with which clients, such as the [plc-data-server](https://github.com/paul-breen/plc-data-server) (PDS), can connect and query simulated PLCs.

See the [API documentation](https://paul-breen.github.io/plc-simulator/) for further details of each of the simulator's components.

## Install

The [package](https://pypi.org/project/plc-simulator/) can be installed from PyPI (note the package distribution name):

```bash
$ pip install plc-simulator
```

## Running the application

The general usage is to call the plcsimulator package main followed by a configuration file.  As a convenience, the package installs a console script called `plcsimulator` that wraps the call to the package main.  Thus the following two command line invocations are identical:

```bash
$ python -m plcsimulator plc-simulator-conf.json
$ plcsimulator plc-simulator-conf.json
```

Specifying the `--help` option, will print the [CLI](https://en.wikipedia.org/wiki/Command-line_interface) usage and quit:

```bash
$ python -m plcsimulator --help 
```

## The configuration

The configuration contains sections that map to components of the simulator.  These sections specify:

* listener: Socket connection parameters such as host and port.
* fieldbus_manager: A list of available fieldbus-specific modules.  Each module configuration in the list specifies:
  + The module and class that provides the fieldbus interface.
  + The TCP port number that maps to the corresponding one specified in the `listener` configuration.
  * (Optional) Static configuration used when instantiating the fieldbus object.
* memory_manager: The size of the required memory space sections.
  + blen: The number of bits in the `bits` section.  This should be a multiple of 8 and will be rounded up to be so if necessary.
  + w16len: The number of 16-bit words in the `words16` section.
  + w32len: The number of 32-bit words in the `words32` section.
  + w64len: The number of 64-bit words in the `words64` section.
* io_manager: A list of simulations to run.  What is specified for each simulation configuration depends on the simulation function, but typically includes:
  + id: (Optional) A meaningful label which is included in logging output.
  + memspace: The memory space section name, starting address, and number of references (`nbits` for `bits` section, `nwords` for `words*` sections) that the simulation should read/write to.
  + source: (Optional) Some simulations require the value from a source `memspace` configuration to act as an input to the simulation function.
  + operands: (Optional) The `operation` function-type simulation requires a list of operands.  An operand can either be a constant value or the value from a source `memspace` configuration.  The operator name must be an operator from the Python [operator library](https://docs.python.org/3/library/operator.html).
  + function: The function type and any static parameters.
  + pause: Time (s) to pause between calls of the simulation.
* logging: A Python logging configuration, provided as input to `logging.config.dictConfig()`.
 
### An example configuration

The following example configuration shows most of the available options:

```json
{
    "listener": {
        "host": "localhost",
        "port": 5555,
        "backlog": 10
    },
    "fieldbus_manager": {
        "modules": [
            {
                "module": "plcsimulator.ModbusModule",
                "class": "ModbusModule",
                "id": "modbus",
                "port": 5555,
                "conf": {}
            }
        ]
    },
    "memory_manager": {
        "memspace": {
            "blen": 64,
            "w16len": 800,
            "w32len": 0,
            "w64len": 0
        }
    },
    "io_manager": {
        "simulations": [
            {
                "memspace": {"section": "words16", "addr": 0, "nwords": 1},
                "function": {"type": "counter"},
                "pause": 0.001
            },
            {
                "memspace": {"section": "words16", "addr": 1, "nwords": 1},
                "function": {"type": "binary"},
                "pause": 5
            },
            {
                "memspace": {"section": "words16", "addr": 2, "nwords": 1},
                "function": {"type": "static", "value": 321},
                "pause": 60
            },
            {
                "memspace": {"section": "words16", "addr": 3, "nwords": 1},
                "function": {"type": "sine"},
                "pause": 0.001
            },
            {
                "memspace": {"section": "words16", "addr": 4, "nwords": 1},
                "function": {"type": "cosine"},
                "pause": 0.001
            },
            {
                "memspace": {"section": "words16", "addr": 5, "nwords": 1},
                "function": {"type": "sawtooth"},
                "pause": 0.001
            },
            {
                "memspace": {"section": "words16", "addr": 6, "nwords": 1},
                "function": {"type": "square"},
                "pause": 0.001
            },
            {
                "id": "range_counter",
                "memspace": {"section": "words16", "addr": 7, "nwords": 1},
                "function": {"type": "counter", "range": [10]},
                "pause": 0.1
            },
            {
                "id": "dec_range_counter",
                "memspace": {"section": "words16", "addr": 8, "nwords": 1},
                "function": {"type": "counter", "range": [10, 0]},
                "pause": 0.1
            },
            {
                "id": "step_range_counter",
                "memspace": {"section": "words16", "addr": 9, "nwords": 1},
                "function": {"type": "counter", "range": [0, 10, 2]},
                "pause": 0.1
            },
            {
                "id": "randrange",
                "memspace": {"section": "words16", "addr": 10, "nwords": 1},
                "function": {"type": "randrange", "range": [50, 61]},
                "pause": 1
            },
            {
                "id": "lognormal",
                "memspace": {"section": "words16", "addr": 11, "nwords": 1},
                "function": {"type": "lognormal"},
                "pause": 1
            },
            {
                "id": "uniform",
                "memspace": {"section": "words16", "addr": 12, "nwords": 1},
                "function": {"type": "uniform"},
                "pause": 1
            },
            {
                "id": "copy_source_0",
                "memspace": {"section": "words16", "addr": 13, "nwords": 1},
                "function": {"type": "binary"},
                "pause": 15
            },
            {
                "id": "copy_source_1",
                "memspace": {"section": "words16", "addr": 14, "nwords": 1},
                "function": {"type": "binary"},
                "pause": 60
            },
            {
                "id": "copy_source_2",
                "memspace": {"section": "words16", "addr": 15, "nwords": 1},
                "function": {"type": "binary"},
                "pause": 20
            },
            {
                "id": "copy_source_3",
                "memspace": {"section": "words16", "addr": 16, "nwords": 1},
                "function": {"type": "counter", "range": [80, 0]},
                "pause": 1
            },
            {
                "id": "copy_dest",
                "memspace": {"section": "words16", "addr": 20, "nwords": 4},
                "source": {
                    "memspace": {"section": "words16", "addr": 13, "nwords": 4}
                },
                "function": {"type": "copy"},
                "pause": 1
            },
            {
                "id": "transform_on",
                "memspace": {"section": "words16", "addr": 24, "nwords": 1},
                "source": {
                    "memspace": {"section": "words16", "addr": 16, "nwords": 1}
                },
                "function": {"type": "transform",
                             "transform": {"in": [0, 10], "out": 1}
                },
                "pause": 1
            },
            {
                "id": "transform_off",
                "memspace": {"section": "words16", "addr": 24, "nwords": 1},
                "source": {
                    "memspace": {"section": "words16", "addr": 16, "nwords": 1}
                },
                "function": {"type": "transform",
                             "transform": {"in": [11, 80], "out": 0}
                },
                "pause": 1
            },
            {
                "id": "op_arg_a",
                "memspace": {"section": "words16", "addr": 30, "nwords": 1},
                "function": {"type": "counter", "range": [1, 11]},
                "pause": 1
            },
            {
                "id": "op_arg_b",
                "memspace": {"section": "words16", "addr": 31, "nwords": 1},
                "function": {"type": "counter", "range": [1, 11]},
                "pause": 1
            },
            {
                "id": "op_add",
                "memspace": {"section": "words16", "addr": 32, "nwords": 1},
                "operands": [
                    {"memspace": {"section": "words16", "addr": 30, "nwords": 1}},
                    {"memspace": {"section": "words16", "addr": 31, "nwords": 1}}
                ],
                "function": {"type": "operation", "operator": "add"},
                "pause": 0.5
            },
            {
                "id": "op_floordiv",
                "memspace": {"section": "words16", "addr": 33, "nwords": 1},
                "operands": [
                    {"memspace": {"section": "words16", "addr": 30, "nwords": 1}},
                    {"value": 2}
                ],
                "function": {"type": "operation", "operator": "floordiv"},
                "pause": 0.5
            },
            {
                "id": "byte_0_bit_0_flip",
                "memspace": {"section": "bits", "addr": 0, "nbits": 1},
                "function": {"type": "binary"},
                "pause": 5
            },
            {
                "id": "byte_0_bit_1_flip",
                "memspace": {"section": "bits", "addr": 1, "nbits": 1},
                "function": {"type": "binary"},
                "pause": 2
            },
            {
                "id": "byte_1_fixed_bits_0_to_2",
                "memspace": {"section": "bits", "addr": 8, "nbits": 8},
                "function": {"type": "static", "value": 7},
                "pause": 60
            },
            {
                "id": "byte_2_range_counter_cycling_bits",
                "memspace": {"section": "bits", "addr": 16, "nbits": 8},
                "function": {"type": "counter", "range": [255]},
                "pause": 0.1
            }
        ]
    },
    "logging": {
        "version": 1,
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": "/dev/null",
                "mode": "a",
                "formatter": "default"
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(threadName)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S"
            },
            "brief": {
                "format": "%(levelname)s %(threadName)s %(message)s"
            }
        }
    }
}
```

