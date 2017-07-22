
# to have global configuration variables
# similar to
# http://effbot.org/pyfaq/how-do-i-share-global-variables-across-modules.htm

from __future__ import print_function

import os
import sys
from collections import OrderedDict

from ruamel.yaml import YAML
import json
# pylint: disable=invalid-name

yaml = YAML()

server_version = '%s - %s' % (sys.platform, '0.0.1a')
pkg_name = "piqueserver"

config = None

def get_default_location():
    path = os.path.join(os.getenv("XDG_CONFIG_HOME", "~/.config"), "piqueserver")
    return os.path.expanduser(path)

class ServerConfiguration(object):
    def __init__(self, config_dir):
        """
        Object that stores the servers configuration
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(self.config_dir, 'config.yaml')
        self.maps_dir = os.path.join(self.config_dir, 'maps')
        self.scripts_dir = os.path.join(self.config_dir, 'scripts')
        # having a list of options will allow dynamically setting them
        # in the future
        self._options = OrderedDict()
        self._config = {}

    def register_option(self, name, default, info, persist=False):
        """
        register a new configuration option

        name: name of the option
        default: default value
        info: text describing the option
        """
        self._options[name] = {
            "default": default,
            "info": info,
        }

    def load_config(self):
        """
        (re) load the configuration from the config file
        """
        try:
            with open(self.config_file) as f:
                self._config = yaml.load(f)
        except IOError as e:
            self.config_file = os.path.splitext(self.config_file)[0] + ".json"
            print("did not find config.yaml, trying {} instead".format(self.config_file))
            try:
                # FIXME: move error handling to outside, since it might be
                # called outside of run() later
                with open(self.config_file) as f:
                    self._config = yaml.load(f)
            except IOError:
                print('Error reading config from {} - {}: '.format(self.config_file, e))
                print('If you haven\'t already, try copying the example config to '
                      'the default location with "piqueserver --copy-config".')
            except ValueError as e:
                print("Error in config file {}: ".format(self.config_file + str(e)))
                sys.exit(1)

    def save_config(self):
        """
        save the configuration to the config file
        """
        raise NotImplementedError("saving config not implemented")

    def get(self, name):
        """
        Get a configuration attribute.

        The default option is deprecated, use it on register_option in the future instead
        """
        try:
            return self._config[name]
        except KeyError:
            default = self._options[name]["default"]
            self._config[name] = default
            return default

    def load_cli_options(self, string):
        self._config.update(yaml.load(string))

    def update(self, options):
        self._config.update(options)

    def get_geoip_path(self):
        return os.path.join(self.config_dir, "data", "GeoLiteCity.dat")

    def get_bans(self):
        with open(os.path.join(self.config_dir, 'bans.txt')) as f:
            return json.load(f)
