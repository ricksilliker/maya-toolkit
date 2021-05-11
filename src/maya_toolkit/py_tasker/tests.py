import unittest
import logging

import tasks
import directives
import blueprints


logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class AbstractDragonflyCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tasks.reload_all_tasks()
        LOG.info(tasks.TASK_CACHE)


class PluginRunCase(AbstractDragonflyCase):
    def setUp(self):
        self.blueprint = blueprints.Blueprint()
        directives.EnvDirective().define_env(self.blueprint, PROJECT_PATH='/Users/rsilliker/test')
