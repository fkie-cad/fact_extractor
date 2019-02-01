from subprocess import call, PIPE, STDOUT


def program_is_callable(command):
    return call('type {}'.format(command), shell=True, stdout=PIPE, stderr=STDOUT) == 0
