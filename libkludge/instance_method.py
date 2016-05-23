#
# Copyright (c) 2010-2016, Fabric Software Inc. All rights reserved.
#

import clang
from clang.cindex import CursorKind, TypeKind
from value_name import ValueName
from result_codec import ResultCodec
from this_codec import ThisCodec
from param_codec import ParamCodec
from symbol_helpers import replace_invalid_chars
import hashlib

class InstanceMethod:

  def __init__(
    self,
    type_mgr,
    namespace_mgr,
    current_namespace_path,
    this_type_info,
    clang_instance_method,
    template_param_type_map,
    ):
    self.name = clang_instance_method.spelling
    self.desc = "Instance method '%s'" % clang_instance_method.displayname
    self.location = "%s:%s" % (clang_instance_method.location.file, clang_instance_method.location.line)

    result_type = clang_instance_method.result_type
    result_resolved_type = template_param_type_map.get(result_type.spelling, None)
    if result_resolved_type:
      result_type = result_resolved_type

    result_cpp_type_expr = namespace_mgr.resolve_cpp_type_expr(current_namespace_path, result_type.spelling)
    self.result = ResultCodec(
      type_mgr.get_dqti(result_cpp_type_expr)
      )

    is_mutable = not clang_instance_method.type.spelling.endswith('const')
    self.this = ThisCodec(this_type_info, is_mutable)

    self.params = []
    param_num = 0
    for child in clang_instance_method.get_children():
        if child.kind == CursorKind.PARM_DECL:
            param_name = child.spelling
            if not param_name:
                param_name = 'arg'+str(param_num)

            param_type = child.type
            param_resolved_type = template_param_type_map.get(param_type.spelling, None)
            if param_resolved_type:
              param_type = param_resolved_type

            param_cpp_type_expr = namespace_mgr.resolve_cpp_type_expr(current_namespace_path, param_type.spelling)
            self.params.append(ParamCodec(
              type_mgr.get_dqti(param_cpp_type_expr),
              param_name
              ))
            param_num += 1

    h = hashlib.md5()
    for param in self.params:
      h.update(param.type_info.edk.name.toplevel)
    self.edk_symbol_name = "_".join([this_type_info.kl.name.compound, self.name, h.hexdigest()])
    self.edk_symbol_name = replace_invalid_chars(self.edk_symbol_name)
