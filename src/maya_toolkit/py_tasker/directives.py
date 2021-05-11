import logging
from collections import OrderedDict

import blueprints
import stages


LOG = logging.getLogger(__name__)


class EnvDirective(object):
    @classmethod
    def define_env(cls, section, **kwargs):
        if not isinstance(section, (blueprints.Blueprint, stages.Stage)):
            raise ValueError('section must be a Blueprint or Stage type object')

        obj = cls()
        for k, v in kwargs.items():
            obj[k.upper()] = v

        section.set_env(obj)

    def __init__(self, **kwargs):
        setattr(self, 'DEBUG', False)
        for name in kwargs:
            setattr(self, name, kwargs[name])

    __hash__ = None

    def __eq__(self, other):
        if not isinstance(other, EnvDirective):
            return NotImplemented
        return vars(self) == vars(other)

    def __ne__(self, other):
        if not isinstance(other, EnvDirective):
            return NotImplemented
        return not (self == other)

    def __contains__(self, key):
        return key in self.__dict__

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def serialize(self):
        result = OrderedDict()
        result.update(self.__dict__)
        return result


class InputDirective(object):
    @classmethod
    def define_input(cls, stage, **kwargs):
        if not isinstance(stage, stages.Stage):
            raise ValueError('section must be a Stage type object')

        if 'name' not in kwargs:
            kwargs['name'] = stage.name

        obj = cls(**kwargs)
        stage.set_input(obj)

        return obj

    def __init__(self, message, name=None, parameters=[], ok='Ok'):
        self._message = message
        self._parameters = parameters
        self._name = name
        self._ok = ok

    def serialize(self):
        result = OrderedDict()
        result['message'] = self._message
        result['name'] = self._name
        result['ok'] = self._ok
        result['parameters'] = []

        return result


class PostDirective(object):
    @classmethod
    def define_post(cls, section, **kwargs):
        if not isinstance(section, (blueprints.Blueprint, stages.Stage)):
            raise ValueError('section must be a Blueprint or Stage type object')

        obj = cls()
        for condition, tasks in kwargs.items():
            if condition not in obj._conditions:
                continue
            for task in tasks:
                obj.add_task(condition, task)

        section.set_post(obj)

        return obj

    def __init__(self):
        self._conditions = dict(Always=[], Success=[], Failed=[], Aborted=[])

    def add_task(self, condition_key, task):
        if condition_key in self._conditions:
            self._conditions[condition_key].append(task)

    def serialize(self):
        result = OrderedDict()
        result['conditions'] = {k: [t.serialize() for t in v] for k, v in self._conditions.items()}

        return result


class WhenDirective(object):
    @classmethod
    def define_when(cls, stage, **kwargs):
        if not isinstance(stage, stages.Stage):
            raise ValueError('section must be a Stage type object')

        obj = cls()
        stage.set_when(obj)

    def serialize(self):
        result = OrderedDict()
        return result