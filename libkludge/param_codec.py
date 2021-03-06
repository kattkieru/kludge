#
# Copyright (c) 2010-2017 Fabric Software Inc. All rights reserved.
#

from conv_codec import ConvCodec
from value_name import ValueName

class ParamCodec:

  def __init__(self, dqti, name):
    self.value_name = ValueName(name)
    self.is_pointer = dqti.dir_qual.is_pointer
    self.is_mutable_indirect = dqti.dir_qual.is_mutable_indirect
    self.conv = ConvCodec(dqti, self.value_name.cpp)

  def __eq__(self, other):
    if not(self.value_name == other.value_name):
      return False
    if not(self.is_pointer == other.is_pointer):
      return False
    if not(self.is_mutable_indirect == other.is_mutable_indirect):
      return False
    if not(self.conv == other.conv):
      return False
    return True
    
  @property
  def will_promote(self):
    return self.conv.will_promote

  @property
  def type_info(self):
    return self.conv.type_info
  
  @property
  def reference_prefix(self):
    return self.conv.reference_prefix
  
  @property
  def take_pointer_prefix(self):
    return self.conv.take_pointer_prefix
  
  @property
  def deref_pointer_prefix(self):
    return self.conv.deref_pointer_prefix

  def _render(self, obj, lang):
    return self.type_info._render("param", obj, lang, {
      "param": self,
      })

  def render_validate_edk(self):
    return self.conv.render_validate_edk()

  def render_edk(self):
    return self._render("edk", "cpp")

  def render_edk_to_lib_decl(self):
    return self._render("edk_to_lib_decl", "cpp")

  def render_kl(self):
    return self._render("kl", "kl")

  def render_lib(self):
    return self._render("lib", "cpp")

  def render_lib_to_edk(self):
    return self._render("lib_to_edk", "cpp")
