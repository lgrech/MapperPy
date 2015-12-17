from mapperpy.one_way_mapper import OneWayMapper

__author__ = 'lgrech'


class ObjectMapper(object):

    def __init__(self, from_left_mapper, from_right_mapper):
        """
        :param from_left_mapper:
        :type from_left_mapper: OneWayMapper
        :param from_right_mapper:
        :type from_right_mapper: OneWayMapper
        """
        self.__from_left_mapper = from_left_mapper
        self.__from_right_mapper = from_right_mapper

    @classmethod
    def from_class(cls, left_class, right_class):
        return ObjectMapper(
            OneWayMapper.for_target_class(right_class),
            OneWayMapper.for_target_class(left_class))

    @classmethod
    def from_prototype(cls, left_proto_obj, right_proto_obj):
        return ObjectMapper(
            OneWayMapper.for_target_prototype(right_proto_obj),
            OneWayMapper.for_target_prototype(left_proto_obj))

    @classmethod
    def for_dict(cls, left_proto_obj):
        return ObjectMapper(
            OneWayMapper.for_target_prototype(left_proto_obj.__dict__),
            OneWayMapper.for_target_prototype(left_proto_obj))

    def map(self, obj):
        if isinstance(obj, self.__from_right_mapper.target_class):
            return self.__from_left_mapper.map(obj)
        elif isinstance(obj, self.__from_left_mapper.target_class):
            return self.__from_right_mapper.map(obj)

        raise ValueError("This mapper does not support {} class".format(obj.__class__.__name__))

    def map_attr_name(self, attr_name):

        mapped_name = self.__get_mapped_name(self.__from_left_mapper, attr_name)
        if mapped_name and self.__get_mapped_name(self.__from_right_mapper, mapped_name) == attr_name:
            return mapped_name

        mapped_name = self.__get_mapped_name(self.__from_right_mapper, attr_name)
        if mapped_name and self.__get_mapped_name(self.__from_left_mapper, mapped_name) == attr_name:
            return mapped_name

        raise ValueError("Can't find mapping for attribute name: {}".format(attr_name))

    def map_attr_value(self, attr_name, attr_value, target_class):

        if self.__from_left_mapper.target_class == target_class:
            return self.__from_left_mapper.map_attr_value(attr_name, attr_value)

        if self.__from_right_mapper.target_class == target_class:
            return self.__from_right_mapper.map_attr_value(attr_name, attr_value)

        raise ValueError("This mapper does not support {} class".format(target_class.__name__))

    def custom_mappings(self, mapping_dict):

        mapping, rev_mapping = self.__get_explicit_mapping(mapping_dict)

        self.__from_left_mapper.custom_mappings(mapping)
        self.__from_right_mapper.custom_mappings(rev_mapping)
        return self

    def nested_mapper(self, mapper):

        if not isinstance(mapper, ObjectMapper):
            raise ValueError("Nested mapper has to be an instance of {}, {} found".format(
                ObjectMapper.__name__, mapper.__class__.__name__))

        left_type = mapper.__from_right_mapper.target_class
        self.__from_left_mapper.nested_mapper(mapper.__from_left_mapper, left_type)

        right_type = mapper.__from_left_mapper.target_class
        self.__from_right_mapper.nested_mapper(mapper.__from_right_mapper, right_type)

        return self

    def left_initializers(self, initializers_dict):
        self.__from_right_mapper.target_initializers(initializers_dict)
        return self

    def right_initializers(self, initializers_dict):
        self.__from_left_mapper.target_initializers(initializers_dict)
        return self

    def options(self, option):
        self.__from_left_mapper.options(option)
        self.__from_right_mapper.options(option)
        return self

    def __repr__(self):
        return "{}->{}".format(self.__from_right_mapper.target_class, self.__from_left_mapper.target_class)

    @classmethod
    def __get_mapped_name(cls, one_way_mapper, attr_name):
        try:
            return one_way_mapper.map_attr_name(attr_name)
        except ValueError:
            return None

    @classmethod
    def __get_explicit_mapping(cls, input_mapping):

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
