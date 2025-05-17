"""
PLC simulation environment
"""

import argparse

from plcsimulator import __version__, PROGNAME
from plcsimulator.App import App

def parse_cmdln():
    """
    Parse the command line

    :returns: An object containing the command line arguments and options
    :rtype: argparse.Namespace
    """

    parser = argparse.ArgumentParser(description='PLC simulation environment', formatter_class=argparse.RawDescriptionHelpFormatter, prog=PROGNAME)
    parser.add_argument('conf_file', help='The full path to a JSON configuration file')
    parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    return args

def main():
    """
    Main function
    """

    args = parse_cmdln()

    app = App(args.conf_file)
    app.run()

if __name__ == '__main__':
    main()

