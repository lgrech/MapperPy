import unittest
from assertpy import assert_that

from mapperpy.test.common_test_classes import *

from mapperpy import ObjectMapper

__author__ = 'lgrech'


class ObjectMapperDictMappingTest(unittest.TestCase):

    def test_map_empty_to_empty_dict(self):
        assert_that(ObjectMapper(TestEmptyClass1, dict).map(TestEmptyClass1())).is_instance_of(dict)
        assert_that(ObjectMapper(TestEmptyClass1, dict).map({})).is_instance_of(TestEmptyClass1)

    def test_map_one_explicit_property(self):
        # given
        mapper = ObjectMapper(TestClassSomeProperty1, dict).custom_mappings(
            {"some_property": "mapped_property"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['mapped_property']).is_equal_to("some_value")

        # when
        mapped_object_rev = mapper.map(dict(mapped_property="other_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object_rev.some_property).is_equal_to("other_value")

    def test_map_one_explicit_property_rev(self):
        # given
        mapper = ObjectMapper(dict, TestClassSomeProperty1).custom_mappings(
            {"mapped_property": "some_property"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(mapped_object).is_instance_of(dict)
        assert_that(mapped_object['mapped_property']).is_equal_to("some_value")

        # when
        mapped_object_rev = mapper.map(dict(mapped_property="other_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object_rev.some_property).is_equal_to("other_value")

    def test_map_multiple_explicit_properties(self):
        # given
        mapper = ObjectMapper(dict, TestClassMappedProperty).custom_mappings(
                            {"some_property": "mapped_property",
                             "some_property_02": "mapped_property_02",
                             "some_property_03": "mapped_property_03"})

        # when
        mapped_object = mapper.map(dict(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassMappedProperty)
        assert_that(mapped_object.mapped_property).is_equal_to("some_value")
        assert_that(mapped_object.mapped_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object.mapped_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

        # when
        mapped_object_rev = mapper.map(TestClassMappedProperty(
            mapped_property="other_value",
            mapped_property_02="other_value_02",
            mapped_property_03="other_value_03",
            unmapped_property2="unmapped_value"))

        # then
        assert_that(mapped_object_rev).is_instance_of(dict)
        assert_that(mapped_object_rev['some_property']).is_equal_to("other_value")
        assert_that(mapped_object_rev['some_property_02']).is_equal_to("other_value_02")
        assert_that(mapped_object_rev['some_property_03']).is_equal_to("other_value_03")
        assert_that(mapped_object_rev).does_not_contain_key('unmapped_property1')


