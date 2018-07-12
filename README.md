## PLC Simulator

This project provides an extensible PLC simulation environment.  The MemoryManager provides a configurable linear memory space that is independent of any particular model of PLC.  The FieldbusManager instantiates configured fieldbus-specific objects that simulate the behaviour of PLCs.  The Listener provides a TCP/IP interface with which clients, such as the plc-data-server (PDS), can connect and query simulated PLCs.

### Running the application

The command line invocation is simple, requiring only the configuration file:

```bash
python plc-simulator.py plc-simulator-conf.json
```

### The configuration

This is an example configuration:

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
                "conf": {}
            }
        ]
    },
    "memory_manager": {
        "memspace": {
            "blen": 0,
            "w16len": 800,
            "w32len": 0,
            "w64len": 0
        },
        "transforms": {
            "bits": [],
            "words16": [],
            "words32": [],
            "words64": []
        }
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
