#
# Copyright (c) 2010-2017 Fabric Software Inc. All rights reserved.
#

from libkludge.type_info import TypeInfo
from libkludge.selector import Selector
from libkludge.dir_qual_type_info import DirQualTypeInfo
from libkludge.cpp_type_expr_parser import *

class FixedArrayTypeInfo(TypeInfo):

  def __init__(self, jinjenv, undq_cpp_type_expr, element_dqti):
    TypeInfo.__init__(
      self,
      jinjenv,
      kl_name_base = element_dqti.type_info.kl.name.base,
      kl_name_suffix = "[%u]%s" % (undq_cpp_type_expr.size, element_dqti.type_info.kl.name.suffix),
      edk_name = "Fabric::EDK::KL::FixedArray< " + element_dqti.type_info.edk.name + ", " + str(undq_cpp_type_expr.size) + " >",
      lib_expr = undq_cpp_type_expr,
      child_dqtis = [element_dqti]
      )

  def build_codec_lookup_rules(self):
    rules = TypeInfo.build_codec_lookup_rules(self)
    rules["conv"]["*"] = "types/builtin/fixed_array/conv"
    rules["result"]["decl_and_assign_lib_begin"] = "types/builtin/fixed_array/result"
    rules["result"]["decl_and_assign_lib_end"] = "types/builtin/fixed_array/result"
    rules["repr"]["assign_lib"] = "types/builtin/fixed_array/repr"
    return rules

class FixedArraySelector(Selector):

  def __init__(self, ext):
    Selector.__init__(self, ext)

  def get_desc(self):
    return "FixedArray"
    
  def maybe_create_dqti(self, type_mgr, cpp_type_expr):
    if isinstance(cpp_type_expr, FixedArrayOf):
      element_dqti = type_mgr.get_dqti(cpp_type_expr.element)
      return DirQualTypeInfo(
        dir_qual.direct,
        FixedArrayTypeInfo(
          self.jinjenv,
          cpp_type_expr.make_unqualified(),
          element_dqti,
          )
        )
    if isinstance(cpp_type_expr, ReferenceTo) \
      and isinstance(cpp_type_expr.pointee, FixedArrayOf) \
      and cpp_type_expr.pointee.is_const:
      element_dqti = type_mgr.get_dqti(cpp_type_expr.pointee.element)
      return DirQualTypeInfo(
        dir_qual.const_ref,
        FixedArrayTypeInfo(
          self.jinjenv,
          cpp_type_expr.pointee.make_unqualified(),
          element_dqti,
          )
        )
