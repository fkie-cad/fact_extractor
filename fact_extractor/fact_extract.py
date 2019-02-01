import logging

from helperFunctions.program_setup import program_setup
from objects.file import FileObject
from unpacker.unpack import Unpacker


def extract(file_path, config):
    fo = FileObject(file_path=file_path)

    unpacker = Unpacker(config)

    extracted_objects = unpacker.unpack(fo)
    logging.debug('unpacking of {} complete: {} files extracted'.format(fo.get_uid(), len(extracted_objects)))

    for extracted_object in extracted_objects:
        print(extracted_object)


def main():
    arguments, config = program_setup('FACT extractor', 'Standalone extraction utility')
    extract(arguments.FILE_PATH, config)

    return 0


if __name__ == '__main__':
    exit(main())
