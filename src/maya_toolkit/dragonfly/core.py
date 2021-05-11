"""The main components of this extension for dragonfly.
"""

# built-ins
import os
import logging
import uuid
import ast
import copy
import time
from collections import OrderedDict

# third party
import yaml
import maya.cmds as cmds

# internal
import mirror_tools.core
import py_tasker.parameters
import py_tasker.tasks
import py_tasker.config

import modules
import node
import errors


LOG = logging.getLogger(__name__)


class MayaTaskSpec(py_tasker.tasks.TaskSpec):
    """TaskSpec specifically for use with Maya related tasks."""
    def __init__(self, task_type, name, **kwargs):
        super(MayaTaskSpec, self).__init__(task_type, name, **kwargs)

        self.mirror = kwargs.get('mirror', False)
        self.group = kwargs.get('group', None)

    @staticmethod
    def duplicate_spec(spec):
        """Create a deepcopy of a TaskSpec object.

        Args:
            spec: A TaskSpec instance

        Returns:
            TaskSpec: New copy with identical Parameter values.
        """
        return copy.deepcopy(spec)

    @staticmethod
    def mirror_name(name):
        """Conviences method to mirror a string.

        Uses mirrorTools utilities.

        Args:
            name: Input name to mirror

        Returns:
            str: Mirrored string name
        """
        return mirror_tools.core.swapMirrorString(name)

    @staticmethod
    def mirror_spec(spec):
        """Mirror a MayaTaskSpec and its Parameter values.

        This creates a new instance of the MayaTaskSpec with mirrored parameter values

        Returns:
            MayaTaskSpec: New copy of the spec with mirrored Parameter values
        """
        spec = MayaTaskSpec.duplicate_spec(spec)

        mUtil = mirror_tools.core.MirrorUtil()

        spec.name = mirror_tools.core.swapMirrorString(spec.name)

        for param in spec.params():
            if spec.task().params[param].paramType == 'string':
                spec[param] = mirror_tools.core.swapMirrorString(spec[param])
            elif spec.task().params[param].paramType == 'node':
                if spec[param]:
                    mirror_node = mUtil.mirror(spec[param].name())
                    spec[param] = node.dfNode.fromName(str(mirror_node[0]))
                else:
                    spec[param] = None
            elif spec.task().params[param].paramType == 'nodeList':
                mirror_nodes = []
                if spec[param]:
                    node_names = [x.name() for x in spec[param]]
                    mirror_nodes = [str(x) for x in mUtil.mirror(node_names)]
                spec[param] = node.dfNode.fromList(mirror_nodes)
            else:
                continue

        return spec


class Blueprint(object):
    """A struct to organize tasks into a build sequence.

    Pretty much a fancy list that also creates a rig hiearchy and logs the build into logical steps. This will validate
    task data and track errors that occur during the build process of each task. A single build is stored in a single
    directory with a unique UUID, so no build ever overwrites another.

    Blueprint builds save out a few key files:
        - character_input.ma: The initial state of the blueprint Maya scene
        - character_output.ma: The final state of the blueprint Maya scene
        - blueprint.yaml: The build sequence is a YAML data format
        - _cache: directory where each task is saved out after it completes its own `run` method

    Notes:
        This is a unique struct for building Maya rigs, and has no intention of being back ported to dragonfly-base

    Attributes:
        rig_categories (list): Category names to be used as the sub group names of the rig hierarchy
    """
    @staticmethod
    def round(value, decimals=3):
        accuracy = pow(10, decimals)

        return int(value * accuracy) / float(accuracy)

    @staticmethod
    def get_output_directory(build_dir):
        scene_name = os.path.basename(cmds.file(q=True, sn=True)).split('.')[0]

        if not scene_name:
            raise ValueError('Unable to start blueprint build because the file has not been saved')

        output_directory = os.path.join(build_dir, '{}-{}'.format(scene_name, uuid.uuid4()))
        return output_directory

    @staticmethod
    def get_cache_directory(output_dir):
        cache_directory = os.path.join(output_dir, '_cache')
        return cache_directory

    def __init__(self, build_dir=None, output_dir=None, cache_dir=None, debug=False):
        """Initialize an empty Blueprint.

        Args:
            build_dir
            output_dir
            cache_dir
        """
        # private attributes
        self._build_dir = build_dir
        self._output_dir = output_dir
        self._cache_dir = cache_dir

        if self._build_dir is None:
            self._build_dir = py_tasker.config.get_build_dir()
        if self._output_dir is None:
            self._output_dir = Blueprint.get_output_directory(self._build_dir).replace(' ', '-')
        if self._cache_dir is None:
            self._cache_dir = Blueprint.get_cache_directory(self._output_dir).replace(' ', '-')

        self._rig = dict()

        self._start_log = dict()
        self._finish_log = dict()

        self._started = False
        self._running = False
        self._finished = False
        self._cancelled = False

        self._tasks = list()
        self._completed_tasks = list()
        self._errors = list()

        # public attributes
        self.current_task = None
        self.debug = debug
        self.num_completed_tasks = 0
        self.num_total_tasks = 0

    def serialize(self):
        """Return a Blueprint as a data object for export.

        Returns:
            OrderedDict: Blueprint and tasks as writable YAML data.
        """
        result = OrderedDict()
        result['tasks'] = [task.serialize() for task in self.tasks]

        return result

    @property
    def rig(self):
        """If a blueprint is unbuilt this returns nothing, if built, returns the rig hierarchy.

        Returns:
            dict: A mapping of top level nodes for the rig hierarchy
        """
        return self._rig

    @property
    def output_directory(self):
        return self._output_dir

    @property
    def blueprint_file(self):
        bp_file = os.path.join(self._output_dir, 'blueprint.yaml')
        if os.path.isfile(bp_file):
            return bp_file

    @property
    def tasks(self):
        """Get all tasks in the Blueprint currently.

        Returns:
            list: Task data objects in order
        """
        return self._tasks

    @property
    def is_finished(self):
        return 'build' in self._finish_log

    def append_task(self, task):
        """Add a task to the end of the queue.

        Args:
            task (tasks.TaskSpec): Task data object

        Returns:
            None
        """
        self._tasks.append(task)
        LOG.debug('Added task `{}` to builder'.format(task.name))

    def insert_task(self, index, task):
        """Insert a task into the queue at the given position.

        Args:
            index (int): Position in the queue for the task to be inserted
            task (tasks.TaskSpec): Task data object

        Returns:
            None
        """
        self._tasks.insert(index, task)
        LOG.debug('Inserted task {} at index {} to builder'.format(task, index))

    def remove_task(self, index):
        """Delete a task based on its a given index which is the position in the queue.

        Args:
            index (int): Index to be removed

        Returns:
            tasks.TaskSpec: The data object for a task
        """
        task = self._tasks.pop(index)
        LOG.debug('Removed task {} at index {} from builder'.format(task, index))
        return task

    def clear_tasks(self):
        """Removes all tasks from the Blueprint task queue.

        Returns:
            None
        """
        self._tasks = []

    def start(self):
        """Validates the Blueprint then runs it.

        Returns:
            None
        """
        if self._finished:
            raise ValueError('Cannot start a finished Blueprint')

        self._started = True
        LOG.info('Started Blueprint Builder...')

        os.makedirs(self._output_dir)
        os.makedirs(self._cache_dir)

        # save out blueprint as data
        export_blueprint(self, os.path.join(self._output_dir, 'blueprint.yaml'))

        # save out the state of the file before building
        cmds.file(os.path.join(self._output_dir, 'character_input.ma'), ea=True, type='mayaAscii', pr=True)

        self.run()

    def finish(self):
        """Saves out the final build rig and stores meta data for finding its build source.

        Returns:
            None
        """
        #cmds.file(os.path.join(self._output_dir, 'character_output.ma'), ea=True, type='mayaAscii')

        lvl = logging.WARNING if len(self._errors) else logging.INFO
        msg = 'Build Report: {0} seconds, {1} errors'.format(self.time_elapsed(), len(self._errors))
        LOG.log(lvl, msg, extra=dict(duration=self.time_elapsed(), scenePath=cmds.file(q=True, sn=True)))

        self.current_task = None
        self._finished = True

    def cache_task(self):
        """Saves out the current state of the in progress rig build into its own Maya file.

        Returns:
            None
        """
        cache_file_name = os.path.join(self._cache_dir, '{}-{}.ma'.format(self.current_task.replace(' ', '-'), uuid.uuid4()))
        #cmds.file(cache_file_name, ea=True, type='mayaAscii')
        scene_link = '<a href="maya://scene/{0}"><font color="aqua">{1}</font></href>'.format(cache_file_name, self.current_task)
        LOG.info('Cached Task: {}'.format(scene_link))

    def _error(self, spec, msg):
        self._errors.append(msg)
        self._log_error(spec, msg)

    def _log_error(self, spec, msg):
        if self.debug:
            LOG.error('{0}'.format(spec.name), exc_info=True)
        else:
            LOG.error('{0} : {1}'.format(spec.name, msg))

    def time_elapsed(self, group='build'):
        if group not in self._start_log:
            return 0
        if group not in self._finish_log:
            return Blueprint.round(time.time() - self._start_log[group])
        return Blueprint.round(self._finish_log[group] - self._start_log[group])

    def build_generator(self):
        yield dict(group='build', start=True)

        progress = dict(current=0, total=len(self._tasks))

        for spec in self._tasks:
            yield dict(group='spec', start=True, spec=spec, **progress)
            self.current_task = spec.name
            if spec.enabled:
                try:
                    spec.run(rig=self._rig)
                except Exception as e:
                    self._error(spec, e)
                finally:
                    self.cache_task()
            progress['current'] += 1
            yield dict(group='spec', finish=True, spec=spec, **progress)

        yield dict(group='build', finish=True, **progress)

    def run(self):
        """Makes the rig, creates the hierarchy, and one by one, builds each task, then saves out the Maya file.

        Returns:
            None
        """
        if not self._started:
            LOG.warning('`Blueprint.start` must be called before running/continuing a build')
            return

        if self._running:
            return

        if self._finished or self._cancelled:
            LOG.warning('Cannot run/continue a finished or cancelled build')
            return

        self._running = True

        builder = self.build_generator()

        while True:
            st = time.time()
            self._build_data = builder.next()
            self._build_data['time'] = '{0:.2f}'.format(time.time() - st)
            LOG.debug(self._build_data)

            if 'group' in self._build_data:
                group = self._build_data['group']
                if 'start' in self._build_data:
                    self._start_log[group] = time.time()
                elif 'finish' in self._build_data:
                    self._finish_log[group] = time.time()

            if self.is_finished:
                self._finished = True
                break

        self._running = False
        if self._finished:
            self.finish()


def export_blueprint(blueprint, output_path):
    """Save out Task data to an external YAML file.

    Args:
        blueprint (Blueprint): The builder object that has the task data that should be exported.
        output_path (str): File path that will be the blueprint file, overwrites existing file if one exists.

    Returns:
        None
    """
    def _dict_representer(dumper, data):
        return dumper.represent_dict(data.items())

    yaml.Dumper.add_representer(OrderedDict, _dict_representer)
    yaml.Dumper.add_representer(str, yaml.representer.SafeRepresenter.represent_str)
    yaml.Dumper.add_representer(unicode, yaml.representer.SafeRepresenter.represent_unicode)
    yaml.Dumper.add_representer(node.dfNode, node.yaml_representer)

    with open(output_path, 'w') as fp:
        yaml.dump(blueprint.serialize(), Dumper=yaml.Dumper, stream=fp, default_flow_style=False)


def import_blueprint(blueprint_file):
    """Import a blueprint yaml file and create a new Blueprint object.

    Args:
        blueprint_file: The file path to an existing yaml blueprint

    Returns:
        Blueprint: New instance with tasks from the blueprint file
    """
    custom_constructors = list()
    dfNode_constructor = ['!dfNode', node.yaml_constructor]
    custom_constructors.append(dfNode_constructor)

    with open(blueprint_file, 'r') as fp:
        bp = py_tasker.tasks.load_yaml_ordered(fp, constructors=custom_constructors)
    return bp


@py_tasker.parameters.AbstractParameter.register_data_type
def is_python(value):
    """Check if value is python code

    Args:
        value: Data

    Returns:
        bool: Whether or not the value is runnable python code
    """
    try:
        ast.parse(value)
    except SyntaxError:
        return False
    return True


@py_tasker.parameters.AbstractParameter.register_data_type
def is_node(value):
    """Check if value is an existing node.

    Args:
        value: Data

    Returns:
        bool: Whether or not the value is a valid Maya node
    """
    if isinstance(value, node.dfNode) and value.exists():
        return True
    return False


@py_tasker.parameters.AbstractParameter.register_data_type
def is_nodeList(value):
    """Check if value is a list of existing node(s).

    Args:
        value: Data

    Returns:
        bool: Whether or not the value is a valid Maya node
    """
    if not isinstance(value, (list, tuple)):
        return False
    if all([True if isinstance(x, node.dfNode) else False for x in value]):
        return True
    return False


def add_dragonfly_menu():
    """Add a menu item to the Rigging menu if it exists, to show the dragonfly ui

    Returns:
        None
    """
    if cmds.about(batch=True):
        return
    if cmds.menu('MayaWindow|MagicLeapMenu|RigMenu', q=True, ex=True):
        rig_menu_items = cmds.menu('MayaWindow|MagicLeapMenu|RigMenu', q=True, ia=True)

        if rig_menu_items is None or 'DragonflyItem' not in rig_menu_items:
            cmds.menuItem('DragonflyItem', label='Dragonfly', parent='MayaWindow|MagicLeapMenu|RigMenu', command='dragonfly_maya.show()')


def setup():
    """Initialize dragonfly-maya extension for dragonfly.

    Returns:
        None
    """
    default_plugin_path = os.path.join(os.path.dirname(__file__), 'plugins').replace('\\', '/')
    LOG.info('Dragonfly Plugin Path:  {}'.format(default_plugin_path))
    if default_plugin_path not in py_tasker.config.get_plugin_paths():
        py_tasker.config.add_plugin_path([default_plugin_path])

    py_tasker.tasks.reload_all_tasks()
    LOG.info('Loaded {} tasks..'.format(len(py_tasker.tasks.TASK_CACHE)))

    add_dragonfly_menu()


def build_maya_blueprint(blueprint, debug=False):
    scene_path = cmds.file(q=True, sn=True)

    if blueprint is None:
        raise errors.DragonflyBuildError('No blueprint provided for dragonfly to build')

    if not scene_path:
        raise errors.DragonflyBuildError('Cannot build, Maya scene has not been saved')

    blueprint.start()

    scene_name = os.path.basename(scene_path)
    new_scene_name = '{0}_built.ma'.format(scene_name.rsplit('.', 1)[0])
    cmds.file(rn=new_scene_name)

    cmds.headsUpMessage('Build Complete')

    cmds.optionVar(sv=['DRAGONFLY_BUILD', scene_path])
    cmds.optionVar(sva=['DRAGONFLY_BUILD', blueprint.blueprint_file])


def open_maya_blueprint():
    if cmds.optionVar(ex='DRAGONFLY_BUILD'):
        scene_path, bp_file = cmds.optionVar(q='DRAGONFLY_BUILD')
        cmds.file(scene_path, o=True, f=True)
        return bp_file
