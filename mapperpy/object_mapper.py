import inspect
from mapper_options import MapperOptions

__author__ = 'lgrech'


class ObjectMapper(object):

    def __init__(self, left_class, right_class, left_prototype_obj=None, right_prototype_obj=None):
        self._left_class = left_class
        self._right_class = right_class
        self._left_prototype_obj = left_prototype_obj
        self._right_prototype_obj = right_prototype_obj
        self._explicit_mapping_from_left = {}
        self._explicit_mapping_from_right = {}
        self._nested_mappers = {}
        self._left_initializers = {}
        self._right_initializers = {}
        self.__general_settings = {}

    @classmethod
    def from_class(cls, left_class, right_class):
        return ObjectMapper(left_class, right_class)

    @classmethod
    def from_prototype(cls, left_proto, right_proto):
        return ObjectMapper(left_proto.__class__, right_proto.__class__, left_proto, right_proto)

    def map(self, obj):

        if isinstance(obj, self._left_class):
            param_dict = self._get_mapped_params_dict(
                obj, self._right_class, self._explicit_mapping_from_left, self._right_initializers,
                self._right_prototype_obj)
            return self._try_create_object(self._right_class, param_dict)

        elif isinstance(obj, self._right_class):
            param_dict = self._get_mapped_params_dict(
                obj, self._left_class, self._explicit_mapping_from_right, self._left_initializers,
                self._left_prototype_obj)
            return self._try_create_object(self._left_class, param_dict)
        else:
            raise ValueError("This mapper does not support {} class".format(obj.__class__.__name__))

    def map_attr_name(self, attr_name):

        if attr_name in self._explicit_mapping_from_left:
            return self._explicit_mapping_from_left[attr_name]

        if attr_name in self._explicit_mapping_from_right:
            return self._explicit_mapping_from_right[attr_name]

        left_proto = self.__try_get_prototype(self._left_prototype_obj, self._left_class)
        if left_proto:
            right_proto = self.__try_get_prototype(self._right_prototype_obj, self._right_class)
            if right_proto and hasattr(left_proto, attr_name) and hasattr(right_proto, attr_name):
                return attr_name

        raise ValueError(attr_name)

    def custom_mappings(self, mapping_dict):
        mapping_from_left, mapping_from_right = self._get_explicit_mapping(mapping_dict)
        self._explicit_mapping_from_left.update(mapping_from_left)
        self._explicit_mapping_from_right.update(mapping_from_right)
        return self

    def nested_mapper(self, mapper):
        self._nested_mappers[mapper._left_class] = mapper
        self._nested_mappers[mapper._right_class] = mapper
        return self

    def left_initializers(self, initializers_dict):
        self._left_initializers.update(initializers_dict)
        return self

    def right_initializers(self, initializers_dict):
        self._right_initializers.update(initializers_dict)
        return self

    def options(self, (setting_name, setting_value)):
        self.__general_settings[setting_name] = setting_value
        return self

    @classmethod
    def _try_create_object(cls, class_, param_dict):
        try:
            return class_(**param_dict)
        except TypeError as er:
            raise AttributeError("Error when initializing class {} with params: {}\n{}".format(
                class_.__name__, param_dict, er.message))

    def _get_mapped_params_dict(self, obj, to_class, explicit_mapping, initializers, prototype_obj=None):

        actual_mapping = self._get_actual_mapping(obj, to_class, explicit_mapping, prototype_obj)

        mapped_params_dict = {}
        try:
            self._apply_mapping(mapped_params_dict, obj, actual_mapping)
            self._apply_initializers(mapped_params_dict, obj, initializers)
            return mapped_params_dict
        except AttributeError as er:
            raise AttributeError("Unknown attribute: {}".format(er.message))

    def _apply_initializers(self, mapped_params_dict, obj, initializers):
        for attr_name, init_func in initializers.items():
            mapped_params_dict[attr_name] = init_func(obj)

    def _apply_mapping(self, mapped_params_dict, obj, actual_mapping):
        for attr_left, attr_right in actual_mapping.items():

            if not (attr_left and attr_right):
                continue

            attr_value = self.__get_attribute(obj, attr_left)

            if type(attr_value) in self._nested_mappers:
                mapped_params_dict[attr_right] = self._nested_mappers[type(attr_value)].map(attr_value)
            else:
                mapped_params_dict[attr_right] = attr_value

    def __get_attribute(self, obj, attr_name):
        try:
            attr_value = getattr(obj, attr_name)
        except Exception as ex:
            if self.__get_setting(MapperOptions.fail_on_get_attr, True):
                raise ex
            return None

        return attr_value

    @classmethod
    def _get_actual_mapping(cls, obj, to_class, explicit_mapping, prototype_obj):

        actual_prototype = cls.__try_get_prototype(prototype_obj, to_class)

        common_attributes = cls._get_common_instance_attributes(obj, actual_prototype) if actual_prototype else []

        actual_mapping = {common_attr: common_attr for common_attr in common_attributes}
        actual_mapping.update(explicit_mapping)

        return actual_mapping

    @classmethod
    def __try_get_prototype(cls, prototype_obj, for_class):

        actual_prototype = prototype_obj

        if not actual_prototype:
            actual_prototype = cls._try_create_prototype(for_class)

        return actual_prototype

    @classmethod
    def _try_create_prototype(cls, to_class):
        try:
            return to_class()
        except TypeError:
            # if we can't instantiate the class then it's not possible to determine instance attributes - implicit
            # mapping won't work
            return None

    @classmethod
    def _get_common_instance_attributes(cls, from_obj, to_obj):
        from_obj_attrs = cls._get_attributes(from_obj)
        to_obj_attrs = cls._get_attributes(to_obj)
        return set(from_obj_attrs).intersection(to_obj_attrs)

    @classmethod
    def _get_attributes(cls, obj):
        attributes = inspect.getmembers(obj, lambda a: not(inspect.isroutine(a)))
        return [attr[0] for attr in attributes if not(attr[0].startswith('__') and attr[0].endswith('__'))]

    @classmethod
    def _get_explicit_mapping(cls, input_mapping):

        mapping = {}
        rev_mapping = {}

        for left, right in input_mapping.items():
            if right is None:
                # user requested to suppress implicit mapping for k
                mapping[left] = rev_mapping[left] = None
            else:
                mapping[left] = right
                rev_mapping[right] = left

        return mapping, rev_mapping

    def __get_setting(self, mapper_option, default_val):
        if mapper_option.get_name() in self.__general_settings:
            return self.__general_settings[mapper_option.get_name()]

        return default_val
