# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=False, name='markdown')
@stringfilter
def my_markdown(value):
    extensions = ["nl2br", "extra", "codehilite", "headerid(level=2)", "sane_lists"]

    return mark_safe(markdown.markdown(force_unicode(value).replace("\\\\", "\\\\\\\\"),
                                       extensions,
                                       safe_mode='escape',
                                       enable_attributes=False,
                                       output_format="html5"))

class MarkdownDemoNode(template.Node):
    def __init__(self, nodelist):
      self.nodelist = nodelist

    def render(self, context):
      input_text = '\n'.join(
        sum(
          map(
            lambda x: map(
              lambda y: y.strip(), x.render(context).split('\n')
            ), self.nodelist), []))
      uid = "d" + hex(abs(hash(input_text)))[2:]
      rendered = my_markdown(input_text)
      input_text = input_text.replace('>', '&gt;').replace('<', '&lt;')
      return """
        <dl class="tabs" data-tab>
          <dd class="active"><a href="#%smd">Markdown</a></dd>
          <dd><a href="#%srender">Aperçu</a></dd>
        </dl>
        <div class="tabs-content">
          <div class="content active" id="%smd"><pre class="codehilite">%s</pre></div>
          <div class="content" id="%srender">%s</div>
        </div>"""%(uid, uid, uid, input_text, uid, rendered)

@register.tag(name='markdown_demo')
def do_comment(parser, token):
    nodelist = parser.parse(('end_markdown_demo',))
    parser.delete_first_token()
    return MarkdownDemoNode(nodelist)
