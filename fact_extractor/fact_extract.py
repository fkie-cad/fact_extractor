import logging
from pathlib import Path

from helperFunctions.program_setup import program_setup
from unpacker.unpack import Unpacker


def extract(file_path, config):
    unpacker = Unpacker(config)

    extracted_objects = unpacker.unpack(file_path)
    logging.info('unpacking of {} complete: {} files extracted'.format(Path(file_path).name, len(extracted_objects)))

    for extracted_object in extracted_objects:
        print(extracted_object)


def main():
    arguments, config = program_setup('FACT extractor', 'Standalone extraction utility')
    extract(arguments.FILE_PATH, config)

    return 0


if __name__ == '__main__':
    exit(main())
