import unittest

from inject.injections import InjectionPoint, AttributeInjection, \
    ParamInjection, NoParamError, NamedAttributeInjection, \
    ClassAttributeInjection, annotated, Tagged, identify
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
        wrapper = ParamInjection.create_wrapper(func)
        
        self.assertTrue(wrapper.func is func)
        self.assertEqual(wrapper.injections, {})
        self.assertTrue(wrapper.injection_wrapper)
    
    def testAddInjection(self):
        '''Add injection should add an injection to the injections dict.'''
        def func(arg): pass
        wrapper = ParamInjection.create_wrapper(func)
        
        ParamInjection.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionNoParamError(self):
        '''Should raise NoParamError when the func does not take an injected param.'''
        def func(): pass
        
        wrapper = ParamInjection.create_wrapper(func)
        self.assertRaises(NoParamError,
                          ParamInjection.add_injection,
                          wrapper, 'arg2', 'inj')
    
    def testAddInjectionArgs(self):
        '''Add injection should not raise NoParamError, when *args given.'''
        def func2(*args): pass
        
        wrapper = ParamInjection.create_wrapper(func2)
        ParamInjection.add_injection(wrapper, 'arg', 'inj')
        self.assertEqual(wrapper.injections['arg'], 'inj')
    
    def testAddInjectionKwargs(self):
        '''Add injection should not raise NoParamError, when **kwargs.'''
        def func3(**kwargs): pass
        
        wrapper = ParamInjection.create_wrapper(func3)
        ParamInjection.add_injection(wrapper, 'kwarg', 'inj')
        self.assertEqual(wrapper.injections['kwarg'], 'inj')


class AnnotatedInjection(unittest.TestCase):
    def setUp(self):
        self.injector = Injector()
        self.injector.register()

    def tearDown(self):
        self.injector.unregister()

    def scenario1(self):
        """basic scenario used by most annotation tests"""

        class A(object): pass

        class B(object): pass

        a = A()
        b = B()
        self.injector.bind(A, a)
        self.injector.bind(B, b)
        return A, a, B, b

    def testInjection(self):
        """ Basic function injection, two parameters, by type
        """
        A, a, B, b = self.scenario1()

        @annotated
        def func(a:A, b:B) -> (A, B):
            return a, b

        a2, b2 = func()
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)

    def testMethodInjection(self):
        """test injection for methods"""
        A, a, B, b = self.scenario1()

        class SomeClass(object):
            @annotated
            def meth(self, a:A, b:B) -> (A, B):
                return a, b

            @classmethod
            @annotated
            def cls_meth(cls, a:A, b:B) -> (A, B):
                return a, b

            @staticmethod
            @annotated
            def static_meth(a:A, b:B) -> (A, B):
                return a, b

        s = SomeClass()
        #call instance method
        a2, b2 = s.meth()
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)

        #call instance method from class attribute
        a2, b2 = SomeClass.meth(s)
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)

        #call classmethod
        a2, b2 = s.cls_meth()
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)

        #call static method
        a2, b2 = s.static_meth()
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)


    def testExcludeNameInjection(self):
        """exclude injection from parameter name"""
        A, a, B, b = self.scenario1()

        @annotated(exclude='param_a')
        def func(param_a:A, param_b:B) -> (A, B):
            return param_a, param_b

        self.assertRaises(TypeError, func)
        a2, b2 = func(a)
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)
        a2, b2 = func(param_a=a)
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)

    def testExcludeTypeInjection(self):
        """Exclude injection by parameter type"""
        A, a, B, b = self.scenario1()

        @annotated(exclude=A)
        def func(param_a:A, param_b:B) -> (A, B):
            return param_a, param_b

        self.assertRaises(TypeError, func)
        a2, b2 = func(a)
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)
        a2, b2 = func(param_a=a)
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)

    def testExcludeTagInjection(self):
        """Exclude injection by tagged type"""
        class A(object): pass

        class B(object): pass

        a1 = A()
        a2 = A()
        b = B()
        self.injector.bind(Tagged(A, 'first'), a1)
        self.injector.bind(Tagged(A, 'second'), a2)
        self.injector.bind(B, b)

        @annotated(exclude=Tagged(A, 'second'))
        def func(first_a:Tagged(A, 'first'),
                 second_a:Tagged(A, 'second'),
                 b:B) -> (A, A, B):
            return first_a, second_a, b

        self.assertRaises(TypeError, func)
        first_a2, second_a2, b2 = func(second_a=a2)
        self.assertEqual(first_a2, a1)
        self.assertEqual(second_a2, a2)
        self.assertEqual(b2, b)

    def testTaggedInjection(self):
        """Tagged annotations hint injections"""
        class A(object): pass

        a1 = A()
        a2 = A()
        self.injector.bind(Tagged(A, 'first'), a1)
        self.injector.bind(Tagged(A, 'second'), a2)

        @annotated
        @identify(param_a2="second")
        def func(param_a1: Tagged(A, 'first'), param_a2: A):
            return param_a1, param_a2

        r1, r2 = func()
        self.assertEqual(r1, a1)
        self.assertEqual(r2, a2)

    def testKwOnlyInjection(self):
        """Kw only function injection"""

        A, a, B, b = self.scenario1()

        @annotated(exclude=A)
        def func(*, param_a:A, param_b:B) -> (A, B):
            return param_a, param_b

        self.assertRaises(TypeError, func)
        self.assertRaises(TypeError, func, a)
        a2, b2 = func(param_a=a)
        self.assertEqual(a2, a)
        self.assertEqual(b2, b)

