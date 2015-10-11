import unittest
from assertpy import assert_that

from mapperpy.mapper_base import MapperBase

__author__ = 'grr07'


class MapperBaseTest(unittest.TestCase):

    def test_map_empty_to_empty(self):
        assert_that(MapperBase(_EmptyClass1, _EmptyClass2).map(_EmptyClass1())).is_instance_of(_EmptyClass2)
        assert_that(MapperBase(_EmptyClass1, _EmptyClass2).map(_EmptyClass2())).is_instance_of(_EmptyClass1)

    def test_map_unknown_class_should_raise_exception(self):
        try:
            MapperBase(_EmptyClass1, _EmptyClass2).map(_OtherClass())
            self.fail("Should raise ValueError")
        except ValueError as er:
            assert_that(er.message).contains(_OtherClass.__name__)

    def test_map_one_explicit_property(self):
        # given
        mapper = _TestMapperSingleProperty(_TestClassExplicit1, _TestClassExplicit2)

        # when
        mapped_object = mapper.map(_TestClassExplicit1(some_property="some_value"))

        # then
        assert_that(mapped_object.mapped_property).is_equal_to("some_value")

        # when
        mapped_object_rev = mapper.map(_TestClassExplicit2(mapped_property="other_value"))

        # then
        assert_that(mapped_object_rev.some_property).is_equal_to("other_value")

    def test_map_unknown_property_should_raise_exception(self):
        # given
        mapper = _TestMapperUnknownProperty1(_TestClassExplicit1, _TestClassExplicit2)

        # when
        try:
            mapper.map(_TestClassExplicit1(some_property="some_value"))
            self.fail("Should raise AttributeError")
        except AttributeError as er:
            # then
            assert_that(er.message).contains("unknown")

        # given
        mapper = _TestMapperUnknownProperty2(_TestClassExplicit1, _TestClassExplicit2)

        # when
        try:
            mapper.map(_TestClassExplicit1(some_property="some_value"))
            self.fail("Should raise AttributeError")
        except AttributeError as er:
            # then
            assert_that(er.message).contains("unknown")

    def test_map_multiple_explicit_properties(self):
        # given
        mapper = _TestMapperMultipleProperties(_TestClassExplicit1, _TestClassExplicit2)

        # when
        mapped_object = mapper.map(_TestClassExplicit1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03"))

        # then
        assert_that(mapped_object.mapped_property).is_equal_to("some_value")
        assert_that(mapped_object.mapped_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object.mapped_property_03).is_equal_to("some_value_03")

        # when
        mapped_object_rev = mapper.map(_TestClassExplicit2(
            mapped_property="other_value",
            mapped_property_02="other_value_02",
            mapped_property_03="other_value_03"))

        # then
        assert_that(mapped_object_rev.some_property).is_equal_to("other_value")
        assert_that(mapped_object_rev.some_property_02).is_equal_to("other_value_02")
        assert_that(mapped_object_rev.some_property_03).is_equal_to("other_value_03")


class _TestMapperMultipleProperties(MapperBase):
    some_property = "mapped_property"
    some_property_02 = "mapped_property_02"
    some_property_03 = "mapped_property_03"


class _TestMapperSingleProperty(MapperBase):
    some_property = "mapped_property"


class _TestMapperUnknownProperty1(MapperBase):
    some_property = "unknown"


class _TestMapperUnknownProperty2(MapperBase):
    unknown = "mapped_property"


class _TestClassExplicit1(object):
    def __init__(self, some_property, some_property_02=None, some_property_03=None):
        self.some_property = some_property
        self.some_property_02 = some_property_02
        self.some_property_03 = some_property_03


class _TestClassExplicit2(object):
    def __init__(self, mapped_property, mapped_property_02=None, mapped_property_03=None):
        self.mapped_property = mapped_property
        self.mapped_property_02 = mapped_property_02
        self.mapped_property_03 = mapped_property_03


class _EmptyClass1(object):
    pass


class _EmptyClass2(object):
    pass


class _OtherClass(object):
    pass
