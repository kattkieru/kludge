#
# Copyright (c) 2010-2016, Fabric Software Inc. All rights reserved.
#

from libkludge.type_info import TypeInfo
from libkludge.selector import Selector
from libkludge.dir_qual_type_info import DirQualTypeInfo
from libkludge.cpp_type_expr_parser import *

const_cpp_type_expr = PointerTo(Const(Void()))
mutable_cpp_type_expr = PointerTo(Void())

class ConstVoidPtrTypeInfo(TypeInfo):

  is_in_place = True

  def __init__(self, jinjenv):
    TypeInfo.__init__(
      self,
      jinjenv,
      name = "Data",
      lib_expr = const_cpp_type_expr,
      )

  def build_codec_lookup_rules(self):
    tds = TypeInfo.build_codec_lookup_rules(self)
    tds["conv"]["*"] = "protocols/conv/builtin/none_cast_away_const"
    tds["result"]["*"] = "protocols/result/builtin/direct"
    return tds

class MutableVoidPtrTypeInfo(TypeInfo):

  is_in_place = True

  def __init__(self, jinjenv):
    TypeInfo.__init__(
      self,
      jinjenv,
      TypeName(
        kl_base = "Data",
        kl_suffix = "",
        edk = "::Fabric::EDK::KL::Data",
        lib_expr = mutable_cpp_type_expr,
        )
      )

  def build_codec_lookup_rules(self):
    tds = TypeInfo.build_codec_lookup_rules(self)
    tds["conv"]["*"] = "protocols/conv/builtin/none"
    tds["result"]["*"] = "protocols/result/builtin/direct"
    return tds

class VoidPtrSelector(Selector):

  def __init__(self, jinjenv):
    Selector.__init__(self, jinjenv)

  def maybe_create_dqti(self, type_mgr, cpp_type_expr):
    if cpp_type_expr == const_cpp_type_expr:
      return DirQualTypeInfo(
        dir_qual.direct,
        ConstVoidPtrTypeInfo(self.jinjenv)
        )
    if cpp_type_expr == mutable_cpp_type_expr:
      return DirQualTypeInfo(
        dir_qual.direct,
        MutableVoidPtrTypeInfo(self.jinjenv)
        )
