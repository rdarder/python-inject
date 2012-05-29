import unittest

from inject.injections import InjectionPoint, AttributeInjection, \
    ParamInjection, NoParamError, NamedAttributeInjection, \
    ClassAttributeInjection, getInjectionWrapper, DecoratorInjection
from inject.injectors import Injector


class InjectionTestCase(unittest.TestCase):

    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def testGetInstance(self):
        '''InjectionPoint should call injector's get_instance method.'''
        class A(object): pass

        a = A()
        self.injector.bind(A, to=a)

        injection_point = InjectionPoint(A)
        a2 = injection_point.get_instance()

        self.assertTrue(a2 is a)


class AttributeInjectionTestCase(unittest.TestCase):

    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def testInjection(self):
        '''AttributeInjection should get an instance from an injection.'''
        class A(object): pass
        class B(object):
            a = AttributeInjection(A)

        a = A()
        self.injector.bind(A, to=a)

        b = B()
        self.assertTrue(b.a is a)

    def testInheritance(self):
        '''AttributeInjection should support inheritance.'''
        class A(object): pass
        class B(object):
            a = AttributeInjection(A)
        class C(B): pass

        a = A()
        self.injector.bind(A, to=a)

        b = B()
        c = C()
        self.assertTrue(b.a is a)
        self.assertTrue(c.a is a)

    def testSettingAttr(self):
        '''AttributeInjection should set an attribute of an object.'''
        class A(object): pass
        class B(object):
            a = AttributeInjection(A)

        a = A()
        self.injector.bind(A, a)

        b = B()
        self.assertTrue(b.a is a)

        a2 = A()
        self.injector.bind(A, a2)

        # It is still a, not a2.
        self.assertTrue(b.a is a)


class NamedAttributeInjectionTestCase(unittest.TestCase):

    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def testInjection(self):
        '''NamedAttributeInjection should get an instance from an injection.'''
        class A(object): pass
        class B(object):
            a = NamedAttributeInjection('a', A)

        a = A()
        self.injector.bind(A, to=a)

        b = B()
        self.assertTrue(b.a is a)

    def testInheritance(self):
        '''NamedAttributeInjection should support inheritance.'''
        class A(object): pass
        class B(object):
            a = NamedAttributeInjection('a', A)
        class C(B): pass

        a = A()
        self.injector.bind(A, to=a)

        b = B()
        c = C()
        self.assertTrue(b.a is a)
        self.assertTrue(c.a is a)

    def testSettingAttr(self):
        '''NamedAttributeInjection should set an attribute of an object.'''
        class A(object): pass
        class B(object):
            a = NamedAttributeInjection('a', A)

        a = A()
        self.injector.bind(A, a)

        b = B()
        self.assertTrue(b.a is a)

        a2 = A()
        self.injector.bind(A, a2)

        # It is still a, not a2.
        self.assertTrue(b.a is a)


class ClassAttributeInjectionTestCase(unittest.TestCase):

    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def testInjection(self):
        '''ClassAttributeInjection should resolve a dependency on every access.'''
        class A(object): pass
        class B(object):
            a = ClassAttributeInjection(A)

        a = A()
        self.injector.bind(A, a)
        self.assertTrue(B.a is a)

        a2 = A()
        self.injector.bind(A, a2)
        self.assertTrue(B.a is a2)


class ParamTestCase(unittest.TestCase):

    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def testInjection(self):
        '''ParamInjection should inject dependencies as kwargs.'''
        class A(object): pass
        a = A()
        self.injector.bind(A, a)

        @ParamInjection('a', A)
        def func(a):
            return a

        self.assertTrue(func() is a)

    def testInjectionNoType(self):
        '''ParamInjection should use name as type when type is not given.'''
        class A(object): pass
        a = A()
        self.injector.bind('a', a)

        @ParamInjection('a')
        def func(a):
            return a

        a2 = func()
        self.assertTrue(a2 is a)

    def testMultipleInjection(self):
        '''Multiple ParamInjection injections should be combined into one.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        self.injector.bind(A, a)
        self.injector.bind(B, b)

        @ParamInjection('a', A)
        @ParamInjection('b', B)
        def func(b, a):
            return b, a

        b2, a2 = func()

        self.assertTrue(b2 is b)
        self.assertTrue(a2 is a)

    def testInjectNonGivenParams(self):
        '''ParamInjection should injection only non-given dependencies.'''
        class A(object): pass
        class B(object): pass
        a = A()
        b = B()
        self.injector.bind(A, a)
        self.injector.bind(B, b)

        @ParamInjection('a', A)
        @ParamInjection('b', B)
        def func(a, b):
            return a, b

        a2, b2 = func(b='b')
        self.assertTrue(a2 is a)
        self.assertEqual(b2, 'b')

    def testCreateWrapper(self):
        '''Create wrapper should return a func with set attributes.'''
        def func(): pass

        wrapper = getInjectionWrapper(func)

        self.assertTrue(wrapper.func is func)
        self.assertEqual(wrapper.param_injections, {})

    def testAddInjection(self):
        '''Add injection should add an injection to the injections dict.'''
        def func(arg): pass
        injection = ParamInjection('arg', 'inj')
        wrapper = injection(func)
        self.assertEqual(wrapper.param_injections['arg'].type, 'inj')

    def testAddInjectionNoParamError(self):
        '''Should raise NoParamError when the func does not take an injected param.'''
        def func(): pass

        injection = ParamInjection('arg2', 'inj')
        self.assertRaises(NoParamError, injection, func)

    def testAddInjectionArgs(self):
        '''Add injection should not raise NoParamError, when *args given.'''
        def func2(*args): pass

        injection = ParamInjection('arg', 'inj')
        wrapper = injection(func2)
        self.assertEqual(wrapper.param_injections['arg'].type, 'inj')

    def testAddInjectionKwargs(self):
        '''Add injection should not raise NoParamError, when **kwargs.'''
        def func3(**kwargs): pass

        injection = ParamInjection('kwarg', 'inj')
        wrapper = injection(func3)
        self.assertEqual(wrapper.param_injections['kwarg'].type, 'inj')


class DecoratorTestCase(unittest.TestCase):

    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def testInjection(self):
        '''DecoratorInjection should inject a decorator to be resolved as a
        dependency .'''
        class ConstantReturnDecorator(object):
            @ParamInjection('ret')
            def __init__(self, ret):
                self.ret = ret
            def __call__(self, func):
                def wrapper(*args, **kwargs):
                    return self.ret
                return wrapper

        @DecoratorInjection(ConstantReturnDecorator)
        def func(n):
            return  n

        self.injector.bind('ret', 10)
        self.assertTrue(func(20) == 10)

    def testDecoratorInlineArgs(self):
        '''Arguments can be provided to a DecoratorInjection. The injected
        decorator gets called with the given arguments before calling
        decorator(func)'''

        class AddBaseOffsetDecorator(object):
            @ParamInjection('base')
            def __init__(self, base):
                self.base = base
            def __call__(self, func, offset):
                def wrapper(n):
                    return func(n + self.base + offset)
                return wrapper

        @DecoratorInjection(AddBaseOffsetDecorator, offset=30)
        def func(n):
            return  n

        self.injector.bind('base', 10)
        self.assertEqual(func(5), 45) #30 + 10 + 5

    def testMethodDecorator(self):
        '''A method with an injected decorator should get called with the
        proper arguments, including 'self' '''

        def PassDecorator():
            def decorator(func):
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper
            return decorator

        class Target(object):
            @DecoratorInjection(PassDecorator)
            def method(self, a):
                return (self, a)

            @DecoratorInjection(PassDecorator)
            @classmethod
            def class_method(cls, a):
                return (cls, a)

            @classmethod #reverse wrapping should transparently work
            @DecoratorInjection(PassDecorator)
            def class_method2(cls, a):
                return (cls, a)

            @DecoratorInjection(PassDecorator)
            @staticmethod
            def static_method(a):
                return a

            @staticmethod #reverse wrapping should transparently work
            @DecoratorInjection(PassDecorator)
            def static_method2(a):
                return a


        t = Target()
        self.assertEqual(t.method(10), (t,10))
        self.assertEqual(t.class_method(10), (Target,10))
        self.assertEqual(t.class_method2(10), (Target,10))
        self.assertEqual(t.static_method(10), 10)
        self.assertEqual(t.static_method2(10), 10)

class MultiBindingTestCase(unittest.TestCase):

    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def testMultiInjection(self):
        '''MultiInjection should inject a MultiBinding(set) of dependencies'''
        @ParamInjection('numbers', 'num')
        def func(numbers):
            return sum(numbers)

        self.injector.add_binding('num', 10)
        self.injector.add_binding('num', 11)
        self.injector.add_binding('num', 12)

        self.assertEqual(func(), 33)

