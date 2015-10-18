================
 MapperPy
================
Python object mapper.

Main features
==============
* can map both ways
* maps automatically matching attributes
* allows to define custom mappings or override default ones
* allows to suppress automatic mapping for specific fields
* allows to provide custom functions for attributes initialization 
* supports nested mappers which are used automatically when attribute of specific type found

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

**Note** that automatic attribute mapping won't work if class(es) can't be instantiated with default no-arg constructor. Class instance is required to determine instance attributes' names.

To overcome this case create mapper from prototype, i.e.::

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

Nested mappers
---------------

Mapping attribute name
-----------------------