"""The attribute system for dragonfly.
"""
import os
import logging
from collections import OrderedDict


LOG = logging.getLogger(__name__)


class AbstractParameter(object):
    """A validator for data used on Tasks.

    Attributes:
        DATA_TYPES: Registry for data types a Parameter could possibly be
    """
    DATA_TYPES = dict()

    def __init__(self, name, paramType=None, defaultValue=None, description=None, choices=None, children=None):
        """Initialize the Parameter.

        Args:
            name (str): Name of the Parameter
            paramType (str): Type of data this Parameter represents
            defaultValue: Initial value for the Parameter
            description (str): Helpful tips or info for the Parameter
            choices: Enumeration Parameter name or name/index mapping
            children: Child Parameter name and type mapping
        """
        self._name = name
        self._defaultValue = defaultValue
        self._value = defaultValue
        self._description = description
        self._paramType = paramType
        self._choices = None
        self._children = None

        self.setChoices(choices)
        self.setChildren(children)

    @classmethod
    def register_data_type(cls, type_check_callback):
        """A decorator to register Parameter callbacks for type checking Parameter values.

        Args:
            type_check_callback: Callable

        Returns:
        """
        name_parts = type_check_callback.__name__.split('_')
        data_type_key = '_'.join([x.lower() for x in name_parts[1:]])
        cls.DATA_TYPES[data_type_key] = type_check_callback

    @property
    def name(self):
        """Return the name of the Parameter.

        Returns:
            str: Name
        """
        return self._name

    @property
    def paramType(self):
        """The representation of data for the Parameter.

        Returns:
            str: Attribute type
        """
        return self._paramType

    @property
    def description(self):
        """Return the long form description that describes the use of the Parameter.

        Returns:
            str: Long description
        """
        return self._description

    @property
    def defaultValue(self):
        """Initial value for the Parameter.

        Returns:
        """
        return self._defaultValue

    @property
    def value(self):
        """Return the current value of the Parameter.

        Returns:
        """
        return self._value

    def setValue(self, value):
        """Set the current value of the Parameter.

        Checks `value` to make sure it conforms to the Parameter type requirements.

        Args:
            value: Data

        Returns:
            None
        """
        valueType = AbstractParameter.DATA_TYPES[value]

        if value is not None and valueType != self.paramType:
            raise TypeError("Expected {}, got {}".format(self.paramType, valueType))

        self._value = value

    def choices(self):
        """Return enumeration type Parameter choices if any.

        Returns:
            dict: Enumeration choice names and index values.
        """
        return self._choices

    def setChoices(self, value):
        """Sets the choices attribute of this Parameter by the given data.

        Args:
            value: Data to convert into valid choices options

        Returns:
            None
        """
        if value is None:
            choices = value
        elif isinstance(value, list):
            choices = {k: n for n, k in enumerate(value)}
        elif isinstance(value, dict):
            choices = value
        else:
            raise ValueError("Choices must be either a list of values, or a mapping of values and titles")

        self._choices = choices

    def children(self):
        """Return the children Parameters if any exist.

        Returns:
            list: Children Parameter objects
        """
        return self._children

    def setChildren(self, value):
        """Set the Parameter's children.

        Args:
            value (list): A nested list of name, type pairs of child Parameters

        Returns:
            None
        """
        if value is None:
            children = value
        elif isinstance(value, list):
            children = OrderedDict()
            for child in value:
                children[child['name']] = AbstractParameter(**child)
        else:
            raise ValueError("Children must be either a list of tuples, with a name and type defined")

        self._children = children

    def validate(self):
        """Check that the current value of a Parameter is useable data for it's type.

        Returns:
            None
        """
        raise NotImplemented


def createParameterMap(params):
    """Create Parameter configuration data into Parameter objects.

    Args:
        params (dict): Parameter configuration data

    Returns:
        dict: A mapping of Parameter names to Parameter objects
    """
    result = OrderedDict()

    for name, attrConfig in params.iteritems():
        param = AbstractParameter(name, **attrConfig)
        result[name] = param

    return result


@AbstractParameter.register_data_type
def is_bool(value):
    """Check if value is a boolean Parameter type.

    Args:
        value: Data

    Returns:
        bool: Whether or not the data given is a boolean Parameter type
    """
    if value is True or value is False:
        return True
    for val in (True, False):
        if str(value) == str(val):
            return True
    return False


@AbstractParameter.register_data_type
def is_float(value):
    """Check if value is a float Parameter type.

    Args:
        value: Data

    Returns:
        bool: Whether or not the data given is a float Parameter type
    """
    if isinstance(value, float):
        if value is float(value):
            return True
    return False


@AbstractParameter.register_data_type
def is_int(value):
    """Check if value is a integer Parameter type.

    Args:
        value: Data

    Returns:
        bool: Whether or not the data given is a integer Parameter type
    """
    if isinstance(value, (int, long)):
        if value is int(value):
            return True
    return False


@AbstractParameter.register_data_type
def is_enum(value):
    """Check if value is a enumeration Parameter type.

    Args:
        value: Data

    Returns:
        bool: Whether or not the data given is a enumeration Parameter type
    """
    if isinstance(value, (list, tuple)) and all([isinstance(x, basestring) for x in value]):
        return True
    if isinstance(value, dict):
        if all([is_int(x) for x in value.keys()]) and all([is_string(x) for x in value.values()]):
            return True
        elif all([is_string(x) for x in value.keys()]) and all([is_int(x) for x in value.values()]):
            return True
    return False


@AbstractParameter.register_data_type
def is_file_path(value):
    """Check if value is a file path Parameter type.

    Args:
        value: Data

    Returns:
        bool: Whether or not the data given is a file path Parameter type
    """
    if is_string(value) and os.path.exists(value):
        return True
    return False


@AbstractParameter.register_data_type
def is_string(value):
    """Check if value is a string Parameter type.

    Args:
        value: Data

    Returns:
        bool: Whether or not the data given is a string Parameter type
    """
    return isinstance(value, basestring)


@AbstractParameter.register_data_type
def is_compound(value):
    """Check if value is a compound Parameter type.

    Args:
        value: Data

    Returns:
        bool: Whether or not the data given is a compound Parameter type
    """
    if isinstance(value, (list, tuple)):
        if all([isinstance(x, OrderedDict) for x in value]):
            return True
    return False
