#
# Copyright (c) 2010-2016, Fabric Software Inc. All rights reserved.
#

ext.add_cpp_quoted_include('WrappedType.hpp')

ty = ext.add_wrapped_type('Wrapper<Class>')
ty.add_ctor(['float', 'std::string const &', 'int'])\
  .add_test("""
Class c(3.14, "hello", 42);
report("c.get_floatValue() = " + c.get_floatValue());
report("c.get_stringValue() = " + c.get_stringValue());
""", """
Class::Class(3.14, hello, 42)
Wrapper::Wrapper(Ty *)
c.get_floatValue() = +3.14
c.get_stringValue() = hello
Wrapper::~Wrapper()
Class::~Class()
""")
ty.add_method('publicMethod')\
  .returns('std::string const &')\
  .add_test("""
Class c(3.14, "hello", 42);
report("c.publicMethod() = " + c.publicMethod());
""", """
Class::Class(3.14, hello, 42)
Wrapper::Wrapper(Ty *)
c.publicMethod() = hello
Wrapper::~Wrapper()
Class::~Class()
""")
ty.set_default_access(MemberAccess.public)
ty.add_member('floatValue', 'float')
ty.add_member('stringValue', 'std::string')
ty.set_default_access(MemberAccess.private)
ty.add_member('pri_intValue', 'int')
ty.add_method(
  'PrintValues',
  params = ['Wrapper<Class> const &'],
  this_access = ThisAccess.static,
  ).add_test("""
Class_PrintValues(Class(1.32, "hoo", 23));
""", """
Class::Class(1.32, hoo, 23)
Wrapper::Wrapper(Ty *)
1.32 hoo 23
Wrapper::~Wrapper()
Class::~Class()
""")
ty.add_get_ind_op('int').add_test("""
Class c(3.14, "foo", -7);
report(c.getAt(56));
""", """
Class::Class(3.14, foo, -7)
Wrapper::Wrapper(Ty *)
Class::operator[] const(56)
-7
Wrapper::~Wrapper()
Class::~Class()
""")
ty.add_set_ind_op('int').add_test("""
Class c(3.14, "foo", -7);
c.setAt(56, 4);
report(c);
""", """
Class::Class(3.14, foo, -7)
Wrapper::Wrapper(Ty *)
Class::operator[](56)
{cpp_ptr:<Opaque>}
Wrapper::~Wrapper()
Class::~Class()
""")

ty = ext.add_wrapped_type('Wrapper<DerivedClass>', extends='Wrapper<Class>')
ty.add_ctor(['int'])
ty.add_const_method('newMethod', 'int')
ty.add_test("""
DerivedClass dc(56);
report("dc.newMethod() = " + dc.newMethod());
report("dc.publicMethod() = " + dc.publicMethod());
Class c = dc;
report("c.publicMethod() = " + c.publicMethod());
""", """
Class::Class(3.14, hello, 56)
DerivedClass::DerivedClass(56)
Wrapper::Wrapper(Ty *)
dc.newMethod() = -9
dc.publicMethod() = hello
Wrapper::Wrapper(Ty *)
c.publicMethod() = hello
Wrapper::~Wrapper()
Wrapper::~Wrapper()
DerivedClass::~DerivedClass()
Class::~Class()
""")

#   Class() {}
#   Class(
#     float _floatValue,
#     std::string const &_stringValue,
#     int _intValue
#     )
#     : floatValue( _floatValue )
#     , stringValue( _stringValue )
#     , pri_intValue( _intValue )
#     {}
#   Class( Class const &that )
#     : floatValue( that.floatValue )
#     , stringValue( that.stringValue )
#     , pri_intValue( that.pri_intValue )
#     {}
#   ~Class() {}

#   Class &operator=( Class const &that )
#   {
#     floatValue = that.floatValue;
#     stringValue = that.stringValue;
#     pri_intValue = that.pri_intValue;
#     return *this;
#   }

#   static void PrintValues( Class const &that )
#   {
#     printf("%.2f %s %d\n", that.floatValue, that.stringValue.c_str(),
#            that.pri_intValue);
#   }

#   void changeValues( Class &that )
#   {
#     floatValue = that.floatValue;
#     stringValue = that.stringValue;
#     pri_intValue = that.pri_intValue;
#   }

#   std::string const &publicMethod() { return stringValue; }

#   std::string getDesc() const {
#     return "stringValue: " + stringValue;
#   }

#   float getMulFloatValue( float x ) const { return x * floatValue; }

#   void exportValues(
#     float &_floatValue,
#     std::string &_stringValue,
#     int &_intValue
#     )
#   {
#     _floatValue = floatValue;
#     _stringValue = stringValue;
#     _intValue = pri_intValue;
#   }

# protected:

#   std::string const &protectedMethod() { return stringValue; }

# private:

#   std::string const &privateMethod() { return stringValue; }

# public:

#   float floatValue;
#   std::string stringValue;

# private:

#   int pri_intValue;
# };

# Class ReturnClass() {
#   return Class( 5.61, "foo", -43 );
# }

# std::vector<Class> ReturnClassVec() {
#   std::vector<Class> result;
#   result.push_back( Class( 1.2, "bar", 64 ) );
#   result.push_back( Class( -97.1, "baz", 164 ) );
#   return result;
# }

# struct StructWithIndirectTypeThatCanInPlace {
#   StructWithIndirectTypeThatCanInPlace( float const &x )
#     : floatValue( x ) {}
#   float const &floatValue;
# };

# StructWithIndirectTypeThatCanInPlace ReturnStructWithIndirectTypeThatCanInPlace() {
#   static float x = 5.76;
#   return StructWithIndirectTypeThatCanInPlace( x );
# }


# require WrappedPtr;

# operator entry() {
#   Class value;
#   report("ReturnClass() = " + ReturnClass());
#   report("ReturnClassVec() = " + ReturnClassVec());

#   value = ReturnClass();
#   report("Before value.SET_floatValue(-12.34): value.GET_floatValue() = " + value.GET_floatValue());
#   value.SET_floatValue(-12.34);
#   report("After value.SET_floatValue(-12.34): value.GET_floatValue() = " + value.GET_floatValue());
#   report("Before value.SET_stringValue('hello'): value.GET_stringValue() = " + value.GET_stringValue());
#   value.SET_stringValue('hello');
#   report("After value.SET_stringValue('hello'): value.GET_stringValue() = " + value.GET_stringValue());

#   report("value.publicMethod() = " + value.publicMethod());
#   report("value.getDesc() = " + value.getDesc());
#   report("value.getMulFloatValue(5.12) = " + value.getMulFloatValue(5.12));

#   Float32 floatValue;
#   String stringValue;
#   SInt32 intValue;
#   value.exportValues(floatValue, stringValue, intValue);
#   report("value.exportValues(...): floatValue = " + floatValue);
#   report("value.exportValues(...): stringValue = " + stringValue);
#   report("value.exportValues(...): intValue = " + intValue);

#   StructWithIndirectTypeThatCanInPlace st =
#     ReturnStructWithIndirectTypeThatCanInPlace();
#   report("st.GET_floatValue() = " + st.GET_floatValue());

#   Class constructor1(1.1, 'myString', 123);
#   constructor1.exportValues(floatValue, stringValue, intValue);
#   report("value.exportValues(...): floatValue = " + floatValue);
#   report("value.exportValues(...): stringValue = " + stringValue);
#   report("value.exportValues(...): intValue = " + intValue);

#   Class constructor2(constructor1);
#   constructor2.exportValues(floatValue, stringValue, intValue);
#   report("value.exportValues(...): floatValue = " + floatValue);
#   report("value.exportValues(...): stringValue = " + stringValue);
#   report("value.exportValues(...): intValue = " + intValue);

#   Class c3(2.2, 'otherString', 456);
#   Class_PrintValues(c3);
#   c3.changeValues(constructor2);
#   Class_PrintValues(c3);
# }