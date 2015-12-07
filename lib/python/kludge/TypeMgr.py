from kludge.type_codecs import *
from kludge import CPPTypeExpr, CPPTypeSpec, TypeSpec, SimpleTypeSpec, TypeCodec, ValueName, Value, TypeInfo
import clang.cindex

class TypeMgr:

  def __init__(self):
    self._type_codecs = []

    self._alias_new_type_specs = []
    self._alias_new_cpp_type_name_to_old_cpp_type_expr = {}

    self._cpp_type_name_to_type_info = {}
    self._cpp_type_expr_parser = CPPTypeExpr.Parser(self._alias_new_cpp_type_name_to_old_cpp_type_expr)

    # 'void' must be explcitly checked for by clients.  This is just hear to
    # make sure that 'void' can be looked up
    self.add_type_info(
      'void',
      SimpleTypeSpec(
        '',
        'void',
        CPPTypeExpr.Void()
        )
      )

    # First so we don't catch in Simple...
    self.add_type_codecs(
      build_c_string_type_codecs()
      )
    self.add_type_codecs(
      build_void_ptr_type_codecs()
      )
    self.add_type_codecs(
      build_simple_type_codecs()
      )
    self.add_type_codecs(
      build_std_string_type_codecs()
      )
    self.add_type_codecs(
      build_std_vector_type_codecs()
      )
    self.add_type_codecs(
      build_std_map_type_codecs()
      )

  def add_type_codec(self, type_codec):
    self._type_codecs.append(type_codec)

  def add_type_codecs(self, type_codecs):
    for type_codec in type_codecs:
      self.add_type_codec(type_codec)

  def add_type_info(self, cpp_type_name, type_info):
    self._cpp_type_name_to_type_info[cpp_type_name] = type_info

  def add_type_alias(self, new_cpp_type_name, old_cpp_type_name):
    old_type_info = self.maybe_get_type_info(old_cpp_type_name)
    if old_type_info:
      new_cpp_type_expr = CPPTypeExpr.Named(new_cpp_type_name)
      new_type_spec = SimpleTypeSpec(
        new_cpp_type_name,
        new_cpp_type_name,
        new_cpp_type_expr,
        )
      self._alias_new_type_specs.append(new_type_spec)
      self._alias_new_cpp_type_name_to_old_cpp_type_expr[new_type_spec.cpp.name] = old_type_info
      return new_type_spec, old_type_info._spec
    else:
      return None, None

  @staticmethod
  def parse_value(value):
    if isinstance(value, CPPTypeExpr.Type):
      cpp_type_expr = value
      cpp_type_name = str(cpp_type_expr)
    elif isinstance(value, basestring):
      cpp_type_expr = None
      cpp_type_name = value
    elif isinstance(value, clang.cindex.Type):
      cpp_type_name = value.spelling
      cpp_type_expr = None
    else:
      raise Exception("unexpected argument type")
    return cpp_type_name, cpp_type_expr

  def maybe_get_type_info(self, value):
    if hasattr(value, '__iter__'):
      result = []
      for v in value:
        r = self.maybe_get_type_info(v)
        if not r:
          return None
        result.append(r)
      return result
    else:
      cpp_type_name, cpp_type_expr = TypeMgr.parse_value(value)
      if not cpp_type_name:
        return TypeInfo.VOID

      type_info = self._cpp_type_name_to_type_info.get(cpp_type_name, None)
      if type_info:
        return type_info

      if not cpp_type_expr:
        try:
          cpp_type_expr = self._cpp_type_expr_parser.parse(cpp_type_name)
        except:
          raise Exception(cpp_type_name + ": malformed C++ type expression")

      for type_codec in self._type_codecs:
        type_spec = type_codec.maybe_match(cpp_type_expr, self)
        if type_spec:
          type_info = TypeInfo(type_codec, type_spec)
          self.add_type_info(cpp_type_name, type_info)
          return type_info

  def get_type_info(self, value):
    type_info = self.maybe_get_type_info(value)
    if type_info:
      return type_info

    cpp_type_name, cpp_type_expr = TypeMgr.parse_value(value)
    raise Exception(cpp_type_name + ": no EDK type association found")

  def convert_clang_params(self, clang_params):
    def mapper(clang_param):
      type_info = self.get_type_info(clang_param.clang_type)
      return type_info.make_codec(ValueName(clang_param.name))
    return map(mapper, clang_params)
