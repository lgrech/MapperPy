__author__ = 'lgrech'


class MapperOption(object):
    def __init__(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def __eq__(self, other):
        if isinstance(other, MapperOption):
            return super(MapperOption, self).__eq__(other)

        return self.__name, other


class MapperOptions(object):
    fail_on_get_attr = MapperOption('fail_on_get_attr')
