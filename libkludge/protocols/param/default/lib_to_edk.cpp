{############################################################################}
{# Copyright (c) 2010-2017 Fabric Software Inc. All rights reserved.        #}
{############################################################################}
{% if param.is_mutable_indirect %}
{{param.conv.render_lib_to_edk()}}
{% endif %}
