import sys
from os import path

from plcsimulator.Configurator import Configurator
from plcsimulator.Listener import Listener

if __name__ == "__main__":
    try:
        conf_file = sys.argv[1]
        configurator = Configurator(conf_file)
        configurator.get_configuration()
        configurator.setup_logging()
    except IndexError:
        progname = path.basename(sys.argv[0])
        print("Usage: {} conf.json".format(progname))
        sys.exit(2)

    try:
        server = Listener(configurator.conf)
        server.service_client_requests()
    except KeyboardInterrupt:
        pass

