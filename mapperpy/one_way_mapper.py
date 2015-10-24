import inspect
from enum import Enum
from mapperpy.mapper_options import MapperOptions
from mapperpy.exceptions import ConfigurationException

__author__ = 'lgrech'


class OneWayMapper(object):

    def __init__(self, target_class, target_prototype_obj=None):
        self.__target_class = target_class
        self.__target_prototype_obj = self.__try_get_prototype(target_prototype_obj, self.__target_class)
        self.__explicit_mapping = {}
        self.__nested_mappers = {}
        self.__target_initializers = {}
        self.__general_settings = {}

    @classmethod
    def for_target_class(cls, target_class):
        return OneWayMapper(target_class)

    @classmethod
    def for_target_prototype(cls, proto_obj):
        return OneWayMapper(proto_obj.__class__, proto_obj)

    def map(self, obj):
        param_dict = self.__get_mapped_params_dict(obj)
        return self.__try_create_target_object(param_dict)

    def map_attr_name(self, attr_name):

        if attr_name in self.__explicit_mapping:
            return self.__explicit_mapping[attr_name]

        if self.__target_prototype_obj and hasattr(self.__target_prototype_obj, attr_name):
            return attr_name

        raise ValueError("Can't find mapping for attribute name: {}".format(attr_name))

    def custom_mappings(self, mapping_dict):
        self.__explicit_mapping.update(mapping_dict)
        return self

    def nested_mapper(self, mapper, for_type):

        if not isinstance(mapper, OneWayMapper):
            raise ValueError("Nested mapper has to be an instance of {}, {} found".format(
                OneWayMapper.__name__, mapper.__class__.__name__))

        if for_type not in self.__nested_mappers:
            self.__nested_mappers[for_type] = set()

        if mapper.target_class in [mpr.target_class for mpr in self.__nested_mappers[for_type]]:
            raise ConfigurationException("Nested mapping {}->{} already defined for this mapper".format(
                    for_type.__name__, mapper.target_class.__name__))

        self.__nested_mappers[for_type].add(mapper)

        return self

    def target_initializers(self, initializers_dict):
        self.__target_initializers.update(initializers_dict)
        return self

    def options(self, (setting_name, setting_value)):
        self.__general_settings[setting_name] = setting_value
        return self

    @property
    def target_class(self):
        return self.__target_class

    def __try_create_target_object(self, param_dict):
        try:
            return self.__target_class(**param_dict)
        except TypeError as er:
            raise AttributeError("Error when initializing class {} with params: {}\n{}".format(
                self.__target_class.__name__, param_dict, er.message))

    def __get_mapped_params_dict(self, obj_from):

        actual_mapping = self.__get_actual_mapping(obj_from)

        mapped_params_dict = {}
        try:
            self.__apply_mapping(mapped_params_dict, obj_from, actual_mapping)
            self.__apply_initializers(mapped_params_dict, obj_from)
            return mapped_params_dict
        except AttributeError as er:
            raise AttributeError("Unknown attribute: {}".format(er.message))

    def __apply_initializers(self, mapped_params_dict, source_obj):
        for attr_name, init_func in self.__target_initializers.items():
            mapped_params_dict[attr_name] = init_func(source_obj)

    def __apply_mapping(self, mapped_params_dict, source_obj, actual_mapping):

        for attr_name_from, attr_name_to in actual_mapping.items():

            # skip since mapping is suppressed by user (attribute_name = None)
            if not (attr_name_from and attr_name_to):
                continue

            attr_value = self.__get_attribute_value(source_obj, attr_name_from)

            from_type = type(attr_value)
            to_type = type(
                self.__get_attribute_value(self.__target_prototype_obj, attr_name_to)) if self.__target_prototype_obj else None

            if from_type in self.__nested_mappers:
                mapped_params_dict[attr_name_to] = self.__try_apply_nested_mapper(
                    attr_value, from_type, attr_name_from, to_type, attr_name_to)
            elif to_type and to_type != from_type:
                mapped_params_dict[attr_name_to] = self.__apply_conversion(from_type, to_type, attr_value)
            else:
                mapped_params_dict[attr_name_to] = attr_value

    def __try_apply_nested_mapper(self, attr_value, from_type, attr_name_from, to_type, attr_name_to):

        if len(self.__nested_mappers[from_type]) == 1:
            return list(self.__nested_mappers[from_type])[0].map(attr_value)
        # TODO - but refactor first
        # elif to_type:
        #     applicable_mappers = [mpr for mpr in nested_mappers[from_type] if mpr.


        raise ConfigurationException("Ambiguous nested mapping for attribute {}->{}. Too many mappings defined for "
                                     "type {}".format(attr_name_from, attr_name_to, from_type.__name__))

    @classmethod
    def __apply_conversion(cls, from_type, to_type, attr_value):
        if issubclass(from_type, Enum):
            return cls.__get_conversion_from_enum(attr_value, to_type)
        elif issubclass(to_type, Enum):
            return cls.__get_conversion_to_enum(attr_value, from_type, to_type)
        return attr_value

    @classmethod
    def __get_conversion_to_enum(cls, attr_value, from_type, to_enum_type):
        if from_type == int:
            return to_enum_type(attr_value)
        elif from_type == str:
            # this tries to get enum item from Enum class
            return getattr(to_enum_type, attr_value)
        return attr_value

    @classmethod
    def __get_conversion_from_enum(cls, attr_value, to_type):
        if to_type == int:
            return attr_value.value
        elif to_type == str:
            return attr_value.name
        return attr_value

    def __get_attribute_value(self, obj, attr_name):
        try:
            attr_value = obj[attr_name] if isinstance(obj, dict) else getattr(obj, attr_name)
        except Exception as ex:
            if self.__get_setting(MapperOptions.fail_on_get_attr, True):
                raise ex
            return None

        return attr_value

    def __get_actual_mapping(self, obj):

        common_attributes = \
            self.__get_common_instance_attributes(obj, self.__target_prototype_obj) if self.__target_prototype_obj else []

        actual_mapping = {common_attr: common_attr for common_attr in common_attributes}
        actual_mapping.update(self.__explicit_mapping)

        return actual_mapping

    @classmethod
    def __try_get_prototype(cls, prototype_obj, for_class):

        actual_prototype = prototype_obj

        if not actual_prototype:
            actual_prototype = cls.__try_create_prototype(for_class)

        return actual_prototype

    @classmethod
    def __try_create_prototype(cls, to_class):
        try:
            return to_class()
        except TypeError:
            # if we can't instantiate the class then it's not possible to determine instance attributes - implicit
            # mapping won't work
            return None

    @classmethod
    def __get_common_instance_attributes(cls, from_obj, to_obj):
        from_obj_attrs = cls.__get_attributes(from_obj)
        to_obj_attrs = cls.__get_attributes(to_obj)
        return set(from_obj_attrs).intersection(to_obj_attrs)

    @classmethod
    def __get_attributes(cls, obj):

        if isinstance(obj, dict):
            return obj.keys()

        attributes = inspect.getmembers(obj, lambda a: not(inspect.isroutine(a)))
        return [attr[0] for attr in attributes if not(attr[0].startswith('__') and attr[0].endswith('__'))]

    def __get_setting(self, mapper_option, default_val):
        if mapper_option.get_name() in self.__general_settings:
            return self.__general_settings[mapper_option.get_name()]

        return default_val
