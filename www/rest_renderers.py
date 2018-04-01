from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.request import is_form_media_type, override_method
from rest_framework.exceptions import ParseError
from django.core.paginator import Page


class VaryBrowsableAPIRenderer(BrowsableAPIRenderer):

    def get_rendered_html_form(self, data, view, method, request):
        # Get serializer from the data
        serializer = getattr(data, 'serializer', None)
        if serializer and not getattr(serializer, 'many', False):
            instance = getattr(serializer, 'instance', None)
            if isinstance(instance, Page):
                instance = None
        else:
            instance = None

        # If this is valid serializer data, and the form is for the same
        # HTTP method as was used in the request then use the existing
        # serializer instance, rather than dynamically creating a new one.
        if request.method == method and serializer is not None:
            try:
                kwargs = {'data': request.data}
            except ParseError:
                kwargs = {}
            existing_serializer = serializer
        else:
            kwargs = {}
            existing_serializer = None

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

            if existing_serializer is not None:
                try:
                    return self.render_form_for_serializer(existing_serializer)
                except TypeError:
                    pass

            if has_serializer:
                if method in ('PUT', 'PATCH'):
                    serializer = view.get_serializer(instance=instance, method=method, **kwargs)
                else:
                    serializer = view.get_serializer(**kwargs, method=method)
            else:
                # at this point we must have a serializer_class
                if method in ('PUT', 'PATCH'):
                    serializer = self._get_serializer(view.serializer_class, view,
                                                      request, instance=instance, **kwargs)
                else:
                    serializer = self._get_serializer(view.serializer_class, view,
                                                      request, **kwargs)

            return self.render_form_for_serializer(serializer)
