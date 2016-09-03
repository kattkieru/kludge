from decl import Decl
from libkludge.value_name import ValueName
from libkludge.cpp_type_expr_parser import *

class Alias(Decl):
  def __init__(
    self,
    extname,
    include_filename,
    location,
    desc,
    new_kl_type_name,
    old_type_info,
    ):
    Decl.__init__(
        self,
        extname,
        include_filename,
        location,
        "Type alias '%s'" % desc
        )
    self.new_kl_type_name = new_kl_type_name
    self.old_type_info = old_type_info

  def jinja_stream_aliases(self, jinjenv, lang):
    return jinjenv.get_template('ast/builtin/alias.template.' + lang).stream(decl = self)