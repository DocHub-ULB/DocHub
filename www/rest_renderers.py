from django.core.paginator import Page

from rest_framework.exceptions import ParseError
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.request import is_form_media_type, override_method


class VaryBrowsableAPIRenderer(BrowsableAPIRenderer):

    def get_rendered_html_form(self, data, view, method, request):
        old_serializer = getattr(data, 'serializer', None)
        if old_serializer and not getattr(old_serializer, 'many', False):
            instance = getattr(old_serializer, 'instance', None)
            if isinstance(instance, Page):
                instance = None
        else:
            instance = None

        if request.method == method and old_serializer is not None:
            try:
                kwargs = {'data': request.data}
            except ParseError:
                kwargs = {}
        else:
            kwargs = {}

        with override_method(view, request, method) as request:
            if not self.show_form_for_method(view, method, request, instance):
                return

            if method in ('DELETE', 'OPTIONS'):
                return True  # Don't actually need to return a form

            has_serializer = getattr(view, 'get_serializer', None)

            if (
                (not has_serializer) or
                not any(is_form_media_type(parser.media_type) for parser in view.parser_classes)
            ):
                return

            if has_serializer:
                if method in ('PUT', 'PATCH'):
                    serializer = view.get_serializer(instance=instance, method=method, **kwargs)
                else:
                    try:
                        serializer = view.get_serializer(method=method, **kwargs)
                    except TypeError:
                        serializer = view.get_serializer(**kwargs)
            else:
                # at this point we must have a serializer_class
                if method in ('PUT', 'PATCH'):
                    serializer = self._get_serializer(view.serializer_class, view,
                                                      request, instance=instance, **kwargs)
                else:
                    serializer = self._get_serializer(view.serializer_class, view,
                                                      request, **kwargs)

            return self.render_form_for_serializer(serializer)
