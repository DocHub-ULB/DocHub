# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe, SafeText

register = template.Library()
youtube_url = re.compile(r'https://(?:www\.)?youtu(?:be\.com/watch/?\?v=|\.be/)([^/<&]+)(?:&.*)?')
youtube_iframe = """
<iframe id="youtube-\\1" type="text/html" width="640" height="420"
  src="http://www.youtube.com/embed/\\1"
  frameborder="0"></iframe>
"""


@register.filter(is_safe=False, name='markdown')
@stringfilter
def my_markdown(value):
    extensions = ["nl2br", "extra", "codehilite", "headerid(level=2)", "sane_lists"]

    html = mark_safe(markdown.markdown(force_text(value).replace("\\\\", "\\\\\\\\"),
                                       extensions,
                                       safe_mode='escape',
                                       enable_attributes=False,
                                       output_format="html5"))
    return SafeText(youtube_url.sub(youtube_iframe, html))


class MarkdownDemoNode(template.Node):
    def __init__(self, nodelist):
      self.nodelist = nodelist

    def render(self, context):
      a = map(
        lambda x: list(map(lambda y: y.strip(), x.render(context).split('\n'))),
        self.nodelist
      )

      input_text = '\n'.join(
        sum(list(a), [])
      )
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
