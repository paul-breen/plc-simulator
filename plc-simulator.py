import sys
from os import path

from plcsimulator.App import App

if __name__ == "__main__":
    try:
        conf_file = sys.argv[1]
    except IndexError:
        progname = path.basename(sys.argv[0])
        print("Usage: {} conf.json".format(progname))
        sys.exit(2)

    app = App(conf_file)
    app.run()

