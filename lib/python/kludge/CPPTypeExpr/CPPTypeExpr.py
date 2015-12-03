from pyparsing import *
import abc

class Type:

  __metaclass__ = abc.ABCMeta

  def __init__(self):
    self.is_const = False
    self.is_volatile = False

  @property
  def is_mutable(self):
    return not self.is_const

  def make_const(self):
    self.is_const = True
    return self

  def make_volatile(self):
    self.is_volatile = True
    return self

  @abc.abstractmethod
  def get_desc(self):
    pass

  @abc.abstractmethod
  def get_unqualified_desc(self):
    pass

  def __str__(self):
    return self.get_desc()

  def __eq__(self, other):
    return type(self) == type(other) \
      and self.is_const == other.is_const \
      and self.is_volatile == other.is_volatile

  def __ne__(self, other):
    return not self == other

class Direct(Type):

  def __init__(self):
    Type.__init__(self)

  def get_desc(self):
    result = ""
    if self.is_const:
      result += "const "
    if self.is_volatile:
      result += "volatile "
    return result + self.get_unqualified_desc()

class Void(Direct):

  def __init__(self):
    Direct.__init__(self)

  def get_unqualified_desc(self):
    return "void"

class Bool(Direct):

  def __init__(self):
    Direct.__init__(self)

  def get_unqualified_desc(self):
    return "bool"

class Numeric(Direct):

  def __init__(self):
    Direct.__init__(self)

class Integer(Numeric):

  def __init__(self):
    Numeric.__init__(self)
    self.is_signed = True

  def make_unsigned(self):
    self.is_signed = False
    return self

  def make_signed(self):
    self.is_signed = True
    return self

  def get_unqualified_desc(self):
    result = ""
    if not self.is_signed:
      result = "unsigned "
    result += self.get_signed_desc()
    return result

  @abc.abstractmethod
  def get_signed_desc(self):
    pass

  def __eq__(self, other):
    return Numeric.__eq__(self, other) \
      and self.is_signed == other.is_signed

class Char(Integer):

  def __init__(self):
    Integer.__init__(self)

  def get_signed_desc(self):
    return "char"

class Short(Integer):

  def __init__(self):
    Integer.__init__(self)

  def get_signed_desc(self):
    return "short"

class Int(Integer):

  def __init__(self):
    Integer.__init__(self)

  def get_signed_desc(self):
    return "int"

class LongLong(Integer):

  def __init__(self):
    Integer.__init__(self)

  def get_signed_desc(self):
    return "long long"

class FloatingPoint(Numeric):

  def __init__(self):
    Numeric.__init__(self)

class Float(FloatingPoint):

  def __init__(self):
    FloatingPoint.__init__(self)

  def get_unqualified_desc(self):
    return "float"

class Double(FloatingPoint):

  def __init__(self):
    FloatingPoint.__init__(self)

  def get_unqualified_desc(self):
    return "double"

class Named(Direct):

  def __init__(self, name):
    Direct.__init__(self)
    self.name = name

  def get_unqualified_desc(self):
    return self.name

  def __eq__(self, other):
    return Direct.__eq__(self, other) \
      and self.name == other.name

class Template(Direct):

  def __init__(self, name, params):
    Direct.__init__(self)
    self.name = name
    self.params = params

  def get_unqualified_desc(self):
    return self.name + "< " + ", ".join(map(
      lambda param: param.get_desc(),
      self.params
      )) + " >"

  def __eq__(self, other):
    return Direct.__eq__(self, other) \
      and self.name == other.name \
      and self.params == other.params

class Indirect(Type):

  def __init__(self, pointee):
    Type.__init__(self)
    self.pointee = pointee

  def get_desc(self):
    result = self.get_unqualified_desc()
    if self.is_const:
      result += " const"
    if self.is_volatile:
      result += " volatile"
    return result

  def __eq__(self, other):
    return Type.__eq__(self, other) \
      and self.pointee == other.pointee

class PointerTo(Indirect):

  def __init__(self, pointee):
    Indirect.__init__(self, pointee)

  def get_unqualified_desc(self):
    return self.pointee.get_desc() + " *"

class ReferenceTo(Indirect):

  def __init__(self, pointee):
    Indirect.__init__(self, pointee)

  def get_unqualified_desc(self):
    return self.pointee.get_desc() + " &"

def Const(ty):
  return ty.make_const()

class Parser:

  tok_ast = Literal("*").suppress()
  tok_amp = Literal("&").suppress()
  tok_colon_colon = Literal("::").suppress()
  tok_langle = Literal("<").suppress()
  tok_rangle = Literal(">").suppress()
  tok_comma = Literal(",").suppress()

  key_void = Keyword("void")
  key_bool = Keyword("bool")
  key_char = Keyword("char")
  key_short = Keyword("short")
  key_int = Keyword("int")
  key_long = Keyword("long")
  key_float = Keyword("float")
  key_double = Keyword("double")
  key_signed = Keyword("signed")
  key_unsigned = Keyword("unsigned")
  key_const = Keyword("const")
  key_volatile = Keyword("volatile")

  ident = And([
    NotAny(key_const),
    NotAny(key_volatile),
    Word(alphas+"_", alphanums+"_"),
    ]).setParseAction(lambda s,l,t: Named(t[0]))

  def __init__(self):

    self.ty_void = self.key_void.setParseAction(lambda s,l,t: Void())
    self.ty_bool = self.key_bool.setParseAction(lambda s,l,t: Bool())
    self.ty_char = self.key_char.setParseAction(lambda s,l,t: Char())
    self.ty_short = self.key_short.setParseAction(lambda s,l,t: Short())
    self.ty_int = self.key_int.setParseAction(lambda s,l,t: Int())
    self.ty_long_long = (self.key_long + self.key_long).setParseAction(lambda s,l,t: LongLong())
    self.ty_unqualified_integer = self.ty_char | self.ty_short | self.ty_int | self.ty_long_long
    self.ty_integer = Forward()
    self.ty_integer << MatchFirst([
      ( self.key_signed + self.ty_integer ).setParseAction(lambda s,l,t: t[1].make_signed()),
      ( self.key_unsigned + self.ty_integer ).setParseAction(lambda s,l,t: t[1].make_unsigned()),
      self.ty_unqualified_integer,
      self.key_signed.setParseAction(lambda s,l,t: Int()),
      self.key_unsigned.setParseAction(lambda s,l,t: Int().make_unsigned()),
      ])
    self.ty_float = self.key_float.setParseAction(lambda s,l,t: Float())
    self.ty_double = self.key_double.setParseAction(lambda s,l,t: Double())
    self.ty_floating_point = self.ty_float | self.ty_double
    self.ty_custom = Forward()
    self.ty_custom << MatchFirst([
      (self.ident + self.tok_colon_colon + self.ty_custom).setParseAction(lambda s,l,t: Named(t[0].name + "::" + t[1].name)),
      self.ident,
      ])

    self.ty_post_qualified = Forward()

    self.ty_templated_params = Forward()
    self.ty_templated_params << MatchFirst([
      self.ty_post_qualified + self.tok_comma + self.ty_templated_params,
      self.ty_post_qualified,
      Empty()
      ])

    def make_template(s,l,t):
      return Template(t[0].name, t[1:])

    self.ty_templated = \
      (self.ty_custom + self.tok_langle + self.ty_templated_params + self.tok_rangle).setParseAction(make_template)

    self.ty_unqualified = MatchFirst([
      self.ty_void,
      self.ty_bool,
      self.ty_integer,
      self.ty_floating_point,
      self.ty_templated,
      self.ty_custom,
      ])

    self.ty_pre_qualified = Forward()
    self.ty_pre_qualified << MatchFirst([
        self.ty_unqualified,
        (self.key_const + self.ty_pre_qualified).setParseAction(lambda s,l,t: t[1].make_const()),
        (self.key_volatile + self.ty_pre_qualified).setParseAction(lambda s,l,t: t[1].make_volatile()),
        ])

    self.ty_post_qualified_NO_LEFT_REC = Forward()
    def make_const(te):
      return te.make_const()
    def make_volatile(te):
      return te.make_volatile()
    def make_pointer(te):
      return PointerTo(te)
    def make_reference(te):
      return ReferenceTo(te)
    self.ty_post_qualified_NO_LEFT_REC << MatchFirst([
      (self.key_const.setParseAction(lambda s,l,t: make_const) + self.ty_post_qualified_NO_LEFT_REC),
      (self.key_volatile.setParseAction(lambda s,l,t: make_volatile) + self.ty_post_qualified_NO_LEFT_REC),
      (self.tok_ast.setParseAction(lambda s,l,t: make_pointer) + self.ty_post_qualified_NO_LEFT_REC),
      (self.tok_amp.setParseAction(lambda s,l,t: make_reference) + self.ty_post_qualified_NO_LEFT_REC),
      Empty(),
      ])
    def make_post_qualified(s, l, t):
      result = t[0]
      for i in range(1, len(t)):
        result = t[i](result)
      return result
    self.ty_post_qualified << \
      (self.ty_pre_qualified + self.ty_post_qualified_NO_LEFT_REC).setParseAction(make_post_qualified)

    self.grammar = self.ty_post_qualified + StringEnd()
    self.grammar.validate()

  def parse(self, cpp_type_name):
    return self.grammar.parseString(cpp_type_name)[0]

if __name__ == "__main__":
  p = Parser()
  for e in [
    "void",
    "const void",
    "int *",
    "signed",
    "unsigned",
    "bool",
    "const bool",
    "volatile const signed unsigned",
    "const uint64_t & const ** volatile &",
    "std::string const &",
    "std::vector<std::string>",
    "some::nested<template::expr<int, another>, yet::another<const volatile void *>>",
    "const std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > &",
    "const",
    "volatile",
    "int int",
    "int * void & const",
    ]:
    try:
      r = str(p.parse(e))
    except Exception as ex:
      r = "ERROR"
      # r += str(ex)
    print "%s -> %s" % (e, r)