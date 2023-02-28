#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import sys

from patsy.core.sync import MissingHeadersError, InvalidStatusCodeError, InvalidTimeError
from patsy.database import DatabaseNotSetError
from patsy.core.db_gateway import DbGateway
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from patsy import commands, version
from importlib import import_module
from pkgutil import iter_modules

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level="DEBUG")


def print_header(subcommand: str) -> None:
    """Generate script header and display it in the console."""
    title = f'Command ran: {subcommand}'
    logging.info(title)


def main() -> None:
    """Parse args and set the chosen sub-command as the default function."""

    # main parser for command line arguments
    parser = argparse.ArgumentParser(
        prog='patsy',
        description='Command-line client for preservation asset tracking system (PATSy)'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        help='Print version number and exit',
        version=version
    )

    parser.add_argument(
        '-d', '--database',
        default=None,
        action='store',
        help='Path to db file (defaults to None)',
    )

    subparsers = parser.add_subparsers(title='commands')

    # load all defined subcommands from the patsy.commands package
    command_modules = {}
    for _finder, name, _ispkg in iter_modules(commands.__path__):  # type: ignore[attr-defined]
        module = import_module(commands.__name__ + '.' + name)
        if hasattr(module, 'configure_cli'):
            module.configure_cli(subparsers)  # type: ignore[attr-defined]
            command_modules[name] = module

    # parse command line args
    args = parser.parse_args()

    # if no subcommand was selected, display the help
    if not hasattr(args, 'cmd_name'):
        parser.print_help()
        sys.exit(0)

    # get the selected subcommand
    command = command_modules[args.cmd_name].Command()  # type: ignore[attr-defined]

    logging.info(f"Command ran: {args.cmd_name}")

    load_dotenv()
    status_code: int = 0

    try:
        gateway = DbGateway(args)
        result = command(args, gateway)
        gateway.close()

        if result:
            sys.stderr.write(result)
            sys.stderr.write('\n\n')

    except DatabaseNotSetError:
        logging.error('The "-d" argument was not set nor was the "PATSY_DATABASE" environment variable.')
        status_code = 1

    except OperationalError as e:
        # Some error messages created contain multiple lines and tabs
        # I'm removing them so that splunk has an easier time parsing them
        error = str(e.orig).replace('\n', ' ').replace('\t', '')
        logging.error(error)
        status_code = 1

    except InvalidStatusCodeError:
        logging.error(
            'An error occurred when using the API. This could be due to the servers, '
            'or the headers provided may be incorrect.'
        )
        status_code = 1

    except MissingHeadersError:
        logging.error(
            'The headers to access the ApTrust API were not set. '
            'Provide them as an argument to the sync command or as environment variables in the shell.'
        )
        status_code = 1

    except InvalidTimeError:
        logging.error(
            'The time arguments provided conflict with each other. '
            'Make sure that the "timeafter" argument is a date that comes before the "timebefore" argument.'
        )
        status_code = 1

    finally:
        logging.info("Done")
        sys.exit(status_code)


if __name__ == "__main__":
    main()
