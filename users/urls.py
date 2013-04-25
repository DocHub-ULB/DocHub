# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.conf.urls import patterns, url
from users.views import join_node, leave_node

urlpatterns = patterns("",
    url(r"^join/(?P<nodeid>\d+)$", 
        join_node,
        name="node_join"),
    
    url(r"^leave/(?P<nodeid>\d+)$", 
        leave_node,
        name="node_leave"),
)
