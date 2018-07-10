###############################################################################
# Project: PLC Simulator
# Purpose: Class to encapsulate the configuration functionality
# Author:  Paul M. Breen
# Date:    2018-07-10
###############################################################################

import json
import logging
import logging.config

class Configurator(object):
    """
    Configuration manager for the PLC simulator
    """

    def __init__(self, conf_file):
        """
        Constructor

        :param conf_file: Path to the configuration file
        :type conf_file: str
        """

        self.conf_file = conf_file
        self.conf = {}

    def get_configuration(self):
        """
        Read the JSON configuration file

        :returns: The configuration
        :rtype: dict
        """

        with open(self.conf_file, "rb") as fp:
            self.conf = json.load(fp)

        return self.conf

    def setup_logging(self):
        """
        Setup logging for the application, as specified in the configuration
        """

        try:
            logging_conf = self.conf["logging"]
            logging.config.dictConfig(logging_conf)
        except KeyError:
            pass

