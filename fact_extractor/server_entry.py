#!/usr/bin/env python3

from helperFunctions.config import get_config_dir
from helperFunctions.program_setup import load_config, setup_logging
from server import AppWrapper


def main():
    config = load_config('{}/main.cfg'.format(get_config_dir()))
    setup_logging(debug=False)

    app = AppWrapper(config).app
    app.run('0.0.0.0', 5000)

    return 0


if __name__ == '__main__':
    exit(main())
