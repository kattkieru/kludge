//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//
// Automatically generated by KLUDGE
// *** DO NOT EDIT ***
//
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

#include <FabricEDK.h>

#define FABRIC_EDK_EXT_{{ ext_name }}_DEPENDENT_EXTS \
  { \
    { 0, 0, 0, 0, 0 } \
  }
IMPLEMENT_FABRIC_EDK_ENTRIES({{ ext_name }})

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//
// Function definitions
//
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

{% for func_stream in gen_func_streams() %}
{{ func_stream | join }}
{% endfor %}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
