import unittest
from assertpy import assert_that

from mapperpy.test.common_test_classes import *

from mapperpy import OneWayMapper, MapperOptions, ConfigurationException

__author__ = 'lgrech'


class OneWayMapperTest(unittest.TestCase):

    def test_map_empty_to_empty(self):
        assert_that(OneWayMapper.for_target_class(TestEmptyClass2).map(TestEmptyClass1())).\
            is_instance_of(TestEmptyClass2)

    def test_map_one_explicit_property(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "mapped_property"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassMappedProperty)
        assert_that(mapped_object.mapped_property).is_equal_to("some_value")

    def test_map_unknown_property_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "unknown"})

        # when
        with self.assertRaises(AttributeError) as context:
            mapper.map(TestClassSomeProperty1(some_property="some_value"))

        # then
        assert_that(context.exception.message).contains("unknown")

    def test_map_multiple_explicit_properties(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
                            {"some_property": "mapped_property",
                             "some_property_02": "mapped_property_02",
                             "some_property_03": "mapped_property_03"})

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(
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

    def test_map_multiple_properties_implicit(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2)

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

    def test_map_implicit_with_prototype_obj(self):
        # given
        mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(None))

        # when
        mapped_object = mapper.map(TestClassSomeProperty1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_02")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

    def test_map_override_implicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2).custom_mappings(
                            {"some_property_02": "some_property_03",
                             "some_property_03": "some_property_02"})

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value",
            some_property_02="some_value_02",
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_03")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_02")
        assert_that(mapped_object.unmapped_property2).is_none()

    def test_nested_mapper_when_wrong_param_type_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_class(TestClassSomeProperty2)

        # when
        with self.assertRaises(ValueError) as context:
            root_mapper.nested_mapper(object(), TestClassSomeProperty1)

        # then
        assert_that(context.exception.message).contains(OneWayMapper.__name__)
        assert_that(context.exception.message).contains("object")

    def test_nested_mapper_when_the_same_mapper_added_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_class(TestClassSomeProperty2)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2),
            TestClassSomePropertyEmptyInit1)

        # when
        with self.assertRaises(ConfigurationException) as context:
            root_mapper.nested_mapper(
                OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2),
                TestClassSomePropertyEmptyInit1)

        # then
        assert_that(context.exception.message).contains(TestClassSomePropertyEmptyInit1.__name__)
        assert_that(context.exception.message).contains(TestClassSomePropertyEmptyInit2.__name__)

    def test_map_with_nested_explicit_mapper(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(None))

        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2), TestClassSomePropertyEmptyInit1)

        # when
        mapped_object = root_mapper.map(TestClassSomeProperty1(
            some_property="some_value",
            some_property_02=TestClassSomePropertyEmptyInit1(
                some_property="nested_value",
                some_property_02="nested_value_02",
                some_property_03="nested_value_03",
                unmapped_property1="unmapped_nested_value"),
            some_property_03="some_value_03",
            unmapped_property1="unmapped_value"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)
        assert_that(mapped_object.some_property).is_equal_to("some_value")
        assert_that(mapped_object.some_property_03).is_equal_to("some_value_03")
        assert_that(mapped_object.unmapped_property2).is_none()

        nested_mapped_obj = mapped_object.some_property_02
        assert_that(nested_mapped_obj).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(nested_mapped_obj.some_property).is_equal_to("nested_value")
        assert_that(nested_mapped_obj.some_property_02).is_equal_to("nested_value_02")
        assert_that(nested_mapped_obj.some_property_03).is_equal_to("nested_value_03")
        assert_that(nested_mapped_obj.unmapped_property2).is_none()

    def test_map_when_ambiguous_nested_mapping_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(None))
        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit2()), TestClassSomePropertyEmptyInit1)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomeProperty2(None)), TestClassSomePropertyEmptyInit1)

        # when
        with self.assertRaises(ConfigurationException) as context:
            root_mapper.map(TestClassSomeProperty1(some_property=TestClassSomePropertyEmptyInit1()))

        # then
        assert_that(context.exception.message).contains("some_property")
        assert_that(context.exception.message).contains("TestClassSomePropertyEmptyInit1")

    def test_map_explicit_when_ambiguous_nested_mapping_should_raise_exception(self):
        # given
        root_mapper = OneWayMapper.for_target_class(TestClassMappedProperty).\
            custom_mappings({"some_property": "mapped_property"})
        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2), TestClassSomePropertyEmptyInit1)
        root_mapper.nested_mapper(
            OneWayMapper.for_target_class(TestClassSomeProperty2), TestClassSomePropertyEmptyInit1)

        with self.assertRaises(ConfigurationException) as context:
            # when
            root_mapper.map(TestClassSomeProperty1(some_property=TestClassSomePropertyEmptyInit1()))

        # then
        assert_that(context.exception.message).contains("some_property")
        assert_that(context.exception.message).contains("mapped_property")
        assert_that(context.exception.message).contains("TestClassSomePropertyEmptyInit1")

    # TODO - but refactor first
    # def test_map_with_multiple_nested_mappings_for_one_attribute_when_target_type_known(self):
    #     # given
    #     root_mapper = ObjectMapper.from_prototype(
    #         TestClassSomeProperty1(None),
    #         TestClassSomeProperty2(some_property=TestClassSomePropertyEmptyInit2()))
    #
    #     root_mapper.nested_mapper(
    #         ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(), TestClassSomeProperty2(None)))
    #     root_mapper.nested_mapper(
    #         ObjectMapper.from_prototype(TestClassSomePropertyEmptyInit1(), TestClassSomePropertyEmptyInit2()))
    #
    #     # when
    #     mapped_object = root_mapper.map(
    #         TestClassSomeProperty1(some_property=TestClassSomePropertyEmptyInit1(some_property_02="nested_value_02")))
    #
    #     # then
    #     assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)
    #
    #     nested_mapped_obj = mapped_object.some_property
    #     assert_that(nested_mapped_obj).is_instance_of(TestClassSomePropertyEmptyInit2)
    #     assert_that(nested_mapped_obj.some_property_02).is_equal_to("nested_value_02")

    def test_map_with_reversed_nested_mapper_should_not_use_nested_mapper(self):
        # given
        root_mapper = OneWayMapper.for_target_prototype(TestClassSomeProperty2(TestClassSomePropertyEmptyInit2()))

        root_mapper.nested_mapper(
            OneWayMapper.for_target_prototype(TestClassSomePropertyEmptyInit1), TestClassSomePropertyEmptyInit2)

        # when
        mapped_object = root_mapper.map(TestClassSomeProperty1(
            some_property=TestClassSomePropertyEmptyInit1(some_property="nested_value")))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty2)
        assert_that(mapped_object.some_property).is_instance_of(TestClassSomePropertyEmptyInit1)
        assert_that(mapped_object.some_property.some_property).is_equal_to("nested_value")

    def test_suppress_implicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2).custom_mappings({"some_property": None})

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value", some_property_02="some_value_02"))

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomePropertyEmptyInit2)
        assert_that(mapped_object.some_property).is_none()
        assert_that(mapped_object.some_property_02).is_equal_to("some_value_02")

    def test_map_with_custom_target_initializers(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedPropertyEmptyInit).target_initializers({
                "mapped_property": lambda obj: obj.some_property + obj.some_property_02,
                "unmapped_property2": lambda obj: "prefix_{}".format(obj.unmapped_property1)
            })

        # when
        mapped_object = mapper.map(TestClassSomePropertyEmptyInit1(
            some_property="some_value", some_property_02="some_value_02", unmapped_property1="unmapped_value"))

        assert_that(mapped_object).is_instance_of(TestClassMappedPropertyEmptyInit)
        assert_that(mapped_object.mapped_property).is_equal_to("some_valuesome_value_02")
        assert_that(mapped_object.unmapped_property2).is_equal_to("prefix_unmapped_value")

    def test_map_with_option_fail_on_get_attr(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomeProperty1).custom_mappings(
            {"non_existing_property": "some_property"}).options(MapperOptions.fail_on_get_attr == False)

        # when
        mapped_object = mapper.map(TestEmptyClass1())

        # then
        assert_that(mapped_object).is_instance_of(TestClassSomeProperty1)
        assert_that(mapped_object.some_property).is_none()

        # given
        mapper_strict = OneWayMapper.for_target_class(TestClassSomeProperty1).custom_mappings(
            {"non_existing_property": "some_property"}).options(MapperOptions.fail_on_get_attr == True)

        # when
        with self.assertRaises(AttributeError) as context:
            mapper_strict.map(TestEmptyClass1())

        # then
        assert_that(context.exception.message).contains("non_existing_property")

    def test_map_attr_name_for_empty_classes_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_class(TestEmptyClass1)

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map_attr_name("unmapped_property")

        # then
        assert_that(context.exception.message).contains("unmapped_property")

    def test_map_attr_name_for_unmapped_explicit_property_should_raise_exception(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "mapped_property"})

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map_attr_name("unmapped_property")

        # then
        assert_that(context.exception.message).contains("unmapped_property")

    def test_map_attr_name_for_explicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassMappedProperty).custom_mappings(
            {"some_property": "mapped_property"})

        # then
        assert_that(mapper.map_attr_name("some_property")).is_equal_to("mapped_property")

    def test_map_attr_name_for_implicit_mapping(self):
        # given
        mapper = OneWayMapper.for_target_class(TestClassSomePropertyEmptyInit2)

        # then
        assert_that(mapper.map_attr_name("some_property")).is_equal_to("some_property")
        assert_that(mapper.map_attr_name("some_property_02")).is_equal_to("some_property_02")
        assert_that(mapper.map_attr_name("some_property_03")).is_equal_to("some_property_03")

        # when
        with self.assertRaises(ValueError) as context:
            mapper.map_attr_name("unmapped_property1")

        # then
        assert_that(context.exception.message).contains("unmapped_property1")
