import inspect

__author__ = 'lgrech'


class MapperBase(object):

    def __init__(self, left_class, right_class):
        self._left_class = left_class
        self._right_class = right_class
        self._attributes_mapping_left = self._get_attributes_mapping_from_class()
        self._attributes_mapping_right = {v: k for k, v in self._attributes_mapping_left.items()}

    def map(self, obj):

        if isinstance(obj, self._left_class):
            param_dict = self._get_param_dict(obj, self._attributes_mapping_left)
            return self._try_create_object(self._right_class, param_dict)
        elif isinstance(obj, self._right_class):
            param_dict = self._get_param_dict(obj, self._attributes_mapping_right)
            return self._try_create_object(self._left_class, param_dict)
        else:
            raise ValueError("This mapper does not support {} class".format(obj.__class__.__name__))

    @classmethod
    def _try_create_object(cls, class_, param_dict):
        try:
            return class_(**param_dict)
        except TypeError as er:
            raise AttributeError(er.message)

    @classmethod
    def _get_param_dict(cls, obj, attributes_mapping):
        try:
            return {attr_right: getattr(obj, attr_left) for attr_left, attr_right in attributes_mapping.items()}
        except AttributeError as er:
            raise AttributeError("Unknown attribute: {}".format(er.message))

    @classmethod
    def _get_attributes_mapping_from_class(cls):
        attributes = inspect.getmembers(cls, lambda a: not(inspect.isroutine(a)))
        return {attr[0]: attr[1] for attr in attributes if not(attr[0].startswith('__') and attr[0].endswith('__'))}
