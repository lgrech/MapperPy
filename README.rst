================
 MapperPy
================
Python object mapper.

Main features
==============
* Can map both ways
* Automatically maps matching attributes
* Allows to define custom mappings or override default ones
* Allows to suppress automatic mapping for specific attributes
* Allows to provide custom functions for attributes initialization
* Supports nested mappers which are used automatically when attribute of specific type found

Usage
======

Installation
------------
::

    pip install MapperPy

Importing
---------
::

    from mapperpy import ObjectMapper

Initialization
---------------

Creating mapper from class::

    mapper = ObjectMapper.from_class(ClassA, ClassB)

**Note** that automatic attribute mapping won't work if class(es) can't be instantiated with default no-arg constructor.
Class instance is required to determine instance attributes' names.

To overcome this create mapper from prototype, i.e.::

    mapper = ObjectMapper.from_prototype(ClassA("proto"), ClassB(None, None))

Prototypes are stored and then used during mapping to determine instance attributes' names.

Invoking mapper
---------------

Simply invoke::

    instance_b = mapper.map(instance_a)

or::
   
    instance_a = mapper.map(instance_b)

Mapper determines type of the instance automatically and maps it other type.

Mapper customization
---------------------

Custom mappings (**custom_mappings()**)::

    mapper = mapper.custom_mappings({"some_property": "mapped_property", "my_property": "other_property"})

Suppress automatic mapping::

    mapper = mapper.custom_mappings({"some_property": None})

Custom attribute initialization using function::

    mapper = mapper.left_initializers({
                "some_property": lambda obj: obj.mapped_property + obj.mapped_property_02,
                "unmapped_property1": lambda obj: "prefix_{}".format(obj.unmapped_property2)})

Those functions will be used during initialization of ClassA (on the "left" side). Similarly *right_initializers* can be
used to define initializers of ClassB (on the "right" side).

Nested mappers
---------------

In case of more complex object structure you can use nested mappers.

Let's say you want to map an object which contains another object which you also want to map automatically. You can
define nested mapper and then attach it to root mapper::

    nested_mapper = ObjectMapper.from_class(NestedClassA, NestedClassB)

    mapper = ObjectMapper.from_class(ClassA, ClassB).nested_mapper(nested_mapper)

Mapping attribute name
-----------------------

If you want to determine mapped name of an attribute you can invoke::

    mapped_name = mapper.map_attr_name("some_property")

For example for mapper::

    mapper = mapper.custom_mappings({"some_property": "mapped_property", "my_property": "other_property"})

result of::

    print(mapper.map_attr_name("some_property"))

will be::

    mapped_property
