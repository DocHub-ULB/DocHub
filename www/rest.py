from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status


class VaryModelViewSet(viewsets.ModelViewSet):
    def get_serializer(self, *args, **kwargs):
        method = kwargs.pop('method', None)
        serializer_class = self.get_serializer_class(method=method)
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self, method=None):
        assert self.serializer_class is not None
        assert self.update_serializer_class is not None
        assert self.create_serializer_class is not None
        if method == "PUT":
            return self.update_serializer_class

        if method == "POST":
            return self.create_serializer_class

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, method="POST")
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        view_serializer = self.get_serializer(serializer.instance)
        headers = self.get_success_headers(view_serializer.data)
        return Response(view_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, method="PUT")
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        view_serializer = self.get_serializer(serializer.instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(view_serializer.data)
