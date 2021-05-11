# built-ins
import argparse

# internal
import batch.core


EXPORT_CMD = """
from fbx_exporter import core
core.export_rigs({rigs}, scene_path=None, output_path={outputPath}, bake_start={bakeStart}, bake_end={bakeEnd})
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--animPath', '-ap', default=None, help='Animation scene file path to export')
    parser.add_argument('--outputPath', '-op', default=None, help='FBX output file path')
    parser.add_argument('--rigs', '-r', default=None, help='Names of rigs that should be exported, if None exports all rigs in scene')
    parser.add_argument('--mayaVersion', '-mv', default=2016.5, type=float, help='Maya version to use')
    parser.add_argument('--bakeStart', '-bs', default=1, type=int, help='First frame to start animation baking from')
    parser.add_argument('--bakeEnd', '-be', default=24, type=int, help='Last frame to end animation baking on')
    parser.add_argument('--**kwargs', '-be', default=24, type=int, help='Last frame to end animation baking on')

    kwargs = parser.parse_args().__dict__
    animPath = kwargs.pop('animPath', None)

    if animPath is None:
        raise ValueError('Export failed, animation file path not given')

    batch.core.run_python_on_scene(py_script=EXPORT_CMD.format(**kwargs), scene_path=animPath, save_scene=False)


if __name__ == '__main__':
    main()

