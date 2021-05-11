# built-ins
import argparse
import logging

# internal
import core

logging.basicConfig()

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pyFile', '-pf', help='Script to run')
    parser.add_argument('--mayaVersion', '-mv', default=2016.5, help='Maya version to use')

    kwargs = parser.parse_args().__dict__
    kw = dict()

    if 'pyFile' not in kwargs:
        raise ValueError('No Python script was supplied')
    else:
        kw['py_script'] = kwargs['pyFile']

    try:
        kwargs['mayaVersion'] = int(kwargs['mayaVersion'])
    except ValueError:
        kwargs['mayaVersion'] = float(kwargs['mayaVersion'])

    kw['maya_version'] = kwargs['mayaVersion']

    output = core.run_python_script(**kw)
    LOG.debug(output)
