from __future__ import print_function, unicode_literals

import os
import shutil
import sys
import argparse
import urllib
import gzip

from piqueserver import cfg

MAXMIND_DOWNLOAD = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'


def copy_config():
    config_source = os.path.dirname(os.path.abspath(__file__)) + '/config'
    print('Attempting to copy example config to %s (origin: %s).' %
          (cfg.config.config_dir, config_source))
    try:
        shutil.copytree(config_source, cfg.config.config_dir)
    except Exception as e:  # pylint: disable=broad-except
        print(e)
        sys.exit(1)

    print('Complete! Please edit the files in %s to your liking.' % cfg.config.config_dir)


def update_geoip(target_dir):
    working_directory = os.path.join(target_dir, 'data/')
    zipped_path = os.path.join(
        working_directory, os.path.basename(MAXMIND_DOWNLOAD))
    extracted_path = os.path.join(working_directory, 'GeoLiteCity.dat')

    if not os.path.exists(target_dir):
        print('Configuration directory does not exist')
        sys.exit(1)

    if not os.path.exists(working_directory):
        os.makedirs(working_directory)

    print('Downloading %s' % MAXMIND_DOWNLOAD)

    # PY3: replace with urllib.requests.urlretrieve
    urllib.urlretrieve(MAXMIND_DOWNLOAD, zipped_path)

    print('Download Complete')
    print('Unpacking...')

    with gzip.open(zipped_path, 'rb') as gz:
        d = gz.read()
        with open(extracted_path, 'wb') as ex:
            ex.write(d)

    print('Unpacking Complete')
    print('Cleaning up...')

    os.remove(zipped_path)


def run_server():
    from piqueserver import server
    server.run()


def main():
    default_location = cfg.get_default_location()

    description = '%s is an open-source Python server implementation ' \
                  'for the voxel-based game "Ace of Spades".' % cfg.pkg_name
    arg_parser = argparse.ArgumentParser(prog=cfg.pkg_name,
                                         description=description)

    arg_parser.add_argument('-c', '--config-file', default=None,
                            help='specify the config file - '
                                 'default is "config.json" in the config dir')

    arg_parser.add_argument('-j', '--json-parameters',
                            help='add extra json parameters '
                                 '(overrides the ones present in the config file)')

    arg_parser.add_argument('-d', '--config-dir', default=default_location,
                            help='specify the directory which contains '
                                 'maps, scripts, etc (in correctly named '
                                 'subdirs) - default is %s' % default_location)

    arg_parser.add_argument('--copy-config', action='store_true',
                            help='copies the default/example config dir to '
                            'its default location or as specified by "-d"')

    arg_parser.add_argument('--update-geoip', action='store_true',
                            help='download the latest geoip database')

    args = arg_parser.parse_args()

    # populate the global config with values from args
    cfg.config = cfg.ServerConfiguration(args.config_dir)

    if args.config_file is not None:
        cfg.config.config_file = args.config_file

    if args.json_parameters:
        try:
            cfg.config.load_cli_options(args.json_parameters)
        except Exception as e:  # pylint: disable=broad-except
            print('Error loading json parameters from the command line')
            print(e)
            sys.exit(1)

    run = True

    # copy config and update geoip can happen at the same time
    # note that sys.exit is called from either of these functions on failure
    if args.copy_config:
        copy_config()
        run = False
    if args.update_geoip:
        update_geoip(cfg.config.config_dir)
        run = False

    # only run the server if other tasks weren't performed
    if run:
        cfg.config.load_config()
        run_server()

if __name__ == "__main__":
    main()
