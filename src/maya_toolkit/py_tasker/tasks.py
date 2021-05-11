"""Task components of dragonfly that store task configuration data.
"""
# built-ins
import os
import types
import logging
from collections import MutableMapping, OrderedDict

# third party
import yaml

# internal
import parameters
import errors
import config


LOG = logging.getLogger(__name__)
TASK_CACHE = {}


class TaskSpecError(Exception):
    """Exception to be used in Task `build.py` files."""
    pass


class TaskSpec(yaml.YAMLObject):
    _tempTask = None

    def __init__(self, task_type, name, **kwargs):
        if isinstance(task_type, basestring):
            self._task = TASK_CACHE[task_type]
        else:
            self._task = task_type

        self.name = name
        self.enabled = True
        self.debug = False

        self._params = OrderedDict()
        for param_name in self._task.params:
            self._params[param_name] = self._task[param_name]

        kw_params = {k: v for k, v in kwargs.items() if k in self._params}
        self._params.update(kw_params)

    def __getitem__(self, item):
        return self._params[item]

    def __setitem__(self, key, value):
        self._params[key] = value

    def task(self):
        return self._task

    def type(self):
        return self._task.task_type

    def params(self):
        return self._params

    def reload(self):
        pass

    def run(self, *args, **kwargs):
        self._task.run(self._params, *args, **kwargs)
        return True

    def setUp(self):
        self._task.setUp(self._params, self)

    def serialize(self):
        result = OrderedDict()

        result['name'] = self.name
        result['task'] = self._task.task_type
        result['enabled'] = self.enabled
        result['debug'] = self.debug

        defaults = ['name', 'task', 'enabled', 'debug']
        others = [k for k in sorted(self.__dict__.keys()) if not k.startswith('_') and k not in defaults]
        for k in others:
            result[k] = self.__dict__[k]

        for param_name in self._task.config['params'].iterkeys():
            result[param_name] = self._params[param_name]

        return result


class TaskFactory(MutableMapping):
    @classmethod
    def from_path(cls, path):
        taskType = os.path.basename(path).split('.task')[0]
        return TaskFactory(taskType, path)

    def __hash__(self):
        return 0

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self._taskType, self._path)

    def __getitem__(self, key):
        return self._params[key].value

    def __setitem__(self, key, value):
        self._params[key].setValue(value)

    def __delitem__(self, key):
        del self._params[key]

    def __len__(self):
        return len(self._params)

    def __iter__(self):
        for name, attr in self._params:
            yield name, attr.value

    def __init__(self, taskType, path):
        self._taskType = taskType
        self._path = path
        self._module = None
        self._config = None
        self._params = OrderedDict()

        self.reload_config()

    @property
    def task_type(self):
        return self._taskType

    @property
    def module(self):
        if self._module is None:
            self.reload_module()
        return self._module

    @property
    def config(self):
        if self._config is None:
            self.reload_config()
        return self._config

    @property
    def params(self):
        return self._params

    def reload(self):
        """
        Reload the Task configuration and module
        """
        self.reload_config()
        self.reload_module()

    def reload_config(self):
        yamlPath = os.path.join(self._path, 'config.yaml')
        if not os.path.exists(yamlPath):
            raise IOError("Missing yaml configuration for task {} at {}".format(self._taskType, self._path))

        with open(yamlPath, 'r') as fp:
            task_config = load_yaml_ordered(fp)

        if 'params' in task_config:
            self._params.update(parameters.createParameterMap(task_config['params']))

        self._config = task_config

    def reload_module(self, force=False):
        if self._module is not None:
            if not force:
                # module hasn't been lazy loaded yet, no need to reload
                return

        # raise error if python file does not exist.
        if not os.path.exists(self._path):
            raise IOError("Missing python module for task {} at {}".format(self._taskType, self._path))

        self._module = types.ModuleType(self._taskType)
        self._module.__file__ = os.path.join(self._path, 'build.py')
        code = open(self._module.__file__, 'r')
        exec code in self._module.__dict__

    def validate(self):
        pass

    def run(self, params, *args, **kwargs):
        self.module.run(params, *args, **kwargs)

    def setUp(self, params, spec):
        if getattr(self.module, 'setUp', None) is None:
            LOG.debug('{} has no `setUp` method, skipping setup'.format(self.task_type))
            return
        self.module.setUp(params, spec)


def create_spec(task_type, name, **kwargs):
    try:
        task = TASK_CACHE[task_type]
        spec = TaskSpec(task, name, **kwargs)
    except KeyError as e:
        raise errors.DragonflyError(e)

    return spec


def load_yaml_ordered(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict, constructors=None):
    """Load in yaml preserving dictionary order.

    Notes:
        > http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts

    Returns:
        dict: yaml data in order defined in file
    """
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

    if constructors is not None:
        for value in constructors:
            OrderedLoader.add_constructor(value[0], value[1])

    return yaml.load(stream, OrderedLoader)


def reload_all_tasks():
    """Reload all available Task plugins from disk.

    Returns:
        None
    """
    searchPaths = config.get_plugin_paths()
    LOG.debug(searchPaths)
    taskPaths = [p for d in searchPaths for p in find_tasks_in_path(d)]
    for taskPath in taskPaths:
        t = TaskFactory.from_path(taskPath)
        TASK_CACHE[t.task_type] = t
        LOG.info(taskPath)


def find_tasks_in_path(path):
    """Return valid task paths in a given directory path.

    Args:
        path (str): Directory to search

    Returns:
        list: Full paths to existing valid tasks
    """
    result = []

    for item in os.listdir(path):
        _path = os.path.join(path, item)
        if os.path.isdir(_path):
            if item.endswith(".task"):
                result.append(_path)
            else:
                result.extend(find_tasks_in_path(_path))
    return result


def reload_tasks(taskTypes):
    """Batch reload a list of Task types.

    Args:
        taskTypes(list): List of Task types to refresh

    Returns:
        None
    """
    print taskTypes
    for taskType in taskTypes:
        if taskType in TASK_CACHE:
            TASK_CACHE[taskType].reload()


def get_task_logger(type=None):
    """Get a logger with a specialize name for the plugins path style.

    Args:
        type: The task type

    Returns:
        logging.Logger
    """
    log = logging.getLogger('{}.plugins.{}'.format(__name__, type))
    handler = logging.StreamHandler()
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    return log
