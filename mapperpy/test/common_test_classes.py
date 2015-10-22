__author__ = 'lgrech'


class TestClassSomePropertyEmptyInit1(object):
    def __init__(self, some_property=None, some_property_02=None, some_property_03=None, unmapped_property1=None):
        self.some_property = some_property
        self.some_property_02 = some_property_02
        self.some_property_03 = some_property_03
        self.unmapped_property1 = unmapped_property1


class TestClassSomePropertyEmptyInit2(object):
    def __init__(self, some_property=None, some_property_02=None, some_property_03=None, unmapped_property2=None):
        self.some_property = some_property
        self.some_property_02 = some_property_02
        self.some_property_03 = some_property_03
        self.unmapped_property2 = unmapped_property2


class TestClassSomeProperty1(object):
    def __init__(self, some_property, some_property_02=None, some_property_03=None, unmapped_property1=None):
        self.some_property = some_property
        self.some_property_02 = some_property_02
        self.some_property_03 = some_property_03
        self.unmapped_property1 = unmapped_property1


class TestClassSomeProperty2(object):
    def __init__(self, some_property, some_property_02=None, some_property_03=None, unmapped_property2=None):
        self.some_property = some_property
        self.some_property_02 = some_property_02
        self.some_property_03 = some_property_03
        self.unmapped_property2 = unmapped_property2


class TestClassMappedProperty(object):
    def __init__(self, mapped_property, mapped_property_02=None, mapped_property_03=None, unmapped_property2=None):
        self.mapped_property = mapped_property
        self.mapped_property_02 = mapped_property_02
        self.mapped_property_03 = mapped_property_03
        self.unmapped_property2 = unmapped_property2


class TestClassMappedPropertyEmptyInit(object):
    def __init__(self, mapped_property=None, mapped_property_02=None, mapped_property_03=None, unmapped_property2=None):
        self.mapped_property = mapped_property
        self.mapped_property_02 = mapped_property_02
        self.mapped_property_03 = mapped_property_03
        self.unmapped_property2 = unmapped_property2


class TestEmptyClass1(object):
    pass


class TestEmptyClass2(object):
    pass


class TestOtherClass(object):
    pass
