import logging
from collections import OrderedDict

import directives


LOG = logging.getLogger(__name__)


class Blueprint(object):
    def __init__(self):
        self._env = None
        self._post = None
        self._stages = list()
        
    @property
    def env(self):
        return self._env

    @property
    def post(self):
        return self._post

    def set_env(self, value):
        if isinstance(value, directives.EnvDirective):
            self._env = value

    def set_post(self, value):
        if isinstance(value, directives.PostDirective):
            self._post = value

    def serialize(self):
        result = OrderedDict()
        result['env'] = self._env.serialize()
        result['post'] = self._post.serialize()
        result['stages'] = [stg.serialize() for stg in self._stages]

        return result

    def run(self):
        while self._stages:
            stg = self._stages.pop(0)
            stg.start()
        self.finish()

    def start(self):
        self.run()

    def finish(self):
        if self._post is not None:
            self._post.run()
