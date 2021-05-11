import py_tasker.tasks
import dragonfly.modules

LOG = py_tasker.tasks.get_task_logger(__name__)


def run(params, rig):
    LOG.debug('Removing Namespaces..')
    dragonfly.modules.remove_namespaces()
