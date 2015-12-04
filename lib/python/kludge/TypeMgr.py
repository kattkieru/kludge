from kludge.type_codecs import *
from kludge import CPPTypeExpr, CPPTypeSpec, TypeSpec, ValueName, Param, TypeInfo

# from edk_param import *

class TypeMgr:

  def __init__(self, jinjenv):
    self._type_codecs = []
    self._cpp_type_name_to_type_info = {}
    self._cpp_type_expr_parser = CPPTypeExpr.Parser()

    # First so we don't catch in Simple...
    self.add_type_codecs(
      c_string_type_codecs(jinjenv)
      )

    # self.add_type_codecs(
    #   simple_type_codecs(jinjenv)
    #   )

    # add_simple_type_codecs(jinjenv)
    # add_std_string_type_codecs(jinjenv)
    # add_std_vector_type_codecs(jinjenv)

  def add_type_codec(self, type_codec):
    self._type_codecs.append(type_codec)

  def add_type_codecs(self, type_codecs):
    for type_codec in type_codecs:
      self.add_type_codec(type_codec)
    
  def maybe_get_type_info(self, cpp_type_name):
    if cpp_type_name == "void":
      return None

    type_info = self._cpp_type_name_to_type_info.get(cpp_type_name, None)
    if type_info:
      return type_info

    try:
      cpp_type_spec = CPPTypeSpec(
        cpp_type_name,
        self._cpp_type_expr_parser.parse(cpp_type_name)
        )
    except:
      raise Exception(cpp_type_name + ": malformed C++ type expression")

    for type_codec in self._type_codecs:
      type_spec = type_codec.maybe_match(cpp_type_spec, self)
      if type_spec:
        type_info = TypeInfo(type_codec, type_spec)
        self._cpp_type_name_to_type_info[cpp_type_name] = type_info
        canon_cpp_type_name = str(cpp_type_spec.expr)
        if canon_cpp_type_name != cpp_type_name:
          canon_cpp_type_spec = CPPTypeSpec(
            canon_cpp_type_name,
            cpp_type_spec.expr
            )
          canon_type_spec = TypeSpec(
            type_spec.kl.base,
            type_spec.kl.suffix,
            type_spec.edk.name,
            canon_cpp_type_spec
            )
          canon_type_info = TypeInfo(
            type_codec,
            canon_cpp_type_spec
            )
          self._cpp_type_name_to_type_info[canon_cpp_type_name] = canon_type_info
        return type_info

  def get_type_info(self, cpp_type_name):
    if cpp_type_name == "void":
      return None

    type_info = self.maybe_get_type_info(cpp_type_name)
    if type_info:
      return type_info

    raise Exception(cpp_type_name + ": no EDK type association found")

  def get_type_info_for_clang_type(self, clang_type):
    return self.get_type_info(clang_type.spelling)

  def convert_clang_params(self, clang_params):
    def mapper(clang_param):
      type_info = self.get_type_info_for_clang_type(clang_param.clang_type)
      return Param(ValueName(clang_param.name), type_info)
    return map(mapper, clang_params)
