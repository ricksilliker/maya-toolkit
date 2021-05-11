import logging
from collections import OrderedDict

import directives


LOG = logging.getLogger(__name__)


class Stage(object):
    def __init__(self, name):
        self._name = name
        self._when = None
        self._env = dict()
        self._input = None
        self._post = None
        self._tasks = list()
        self._skipped_tasks = list()
        self._completed_tasks = list()
        self._uncompleted_tasks = list()
        self._blueprint = None

    @property
    def name(self):
        return self._name

    def set_name(self, value):
        if isinstance(value, basestring):
            self._name = value

    @property
    def when(self):
        return self._when

    @property
    def env(self):
        return self._env

    @property
    def input(self):
        return self._input

    @property
    def post(self):
        return self._post

    def parse_env(self):
        e = dict()
        e.update(self._blueprint.env.__dict__)
        e.update(self.env.__dict__)
        return e

    def set_when(self, value):
        if isinstance(value, directives.WhenDirective):
            self._when = value

    def set_env(self, value):
        if isinstance(value, directives.EnvDirective):
            self._env = value

    def set_input(self, value):
        if isinstance(value, directives.InputDirective):
            self._input = value

    def set_post(self, value):
        if isinstance(value, directives.PostDirective):
            self._post = value

    def append_task(self, task):
        self._tasks = task

    def insert_task(self, index, task):
        self._tasks.insert(index, task)

    def remove_task(self, index):
        return self._tasks.pop(index)

    def clear_tasks(self):
        self._tasks = list()

    def serialize(self):
        result = OrderedDict()
        result['name'] = self._name
        result['post'] = self._post.serialize()
        result['env'] = self._env.serialize()
        result['input'] = self._input.serialize()
        result['when'] = self._when.serialize()
        result['tasks'] = [task.serialize() for task in self._tasks]

        return result

    def start(self):
        if self._when is not None and not self._when.run():
            return

        if self._input is not None:
            self._input.run()

        self.run()

    def finish(self):
        if self._post is not None:
            self._post.run()

    def run(self):
        while self._tasks:
            tsk = self._tasks.pop(0)
            if not tsk.enabled:
                self._skipped_tasks.append(tsk)
                continue
            try:
                tsk.run(**self.parse_env())
                self._completed_tasks.append(tsk)
            except Exception as e:
                LOG.exception('Could not complete task {}: \n {}'.format(tsk.name, e))
                self._uncompleted_tasks.append(tsk)
