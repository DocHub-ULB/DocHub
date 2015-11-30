from rest_framework_extensions.routers import NestedRouterMixin
from rest_framework.routers import DefaultRouter

import users.rest
import documents.rest
import catalog.rest


class SimpleRouterWithNesting(NestedRouterMixin, DefaultRouter):
    pass

router = SimpleRouterWithNesting()

router.register(r'users', users.rest.UserViewSet)
router.register(r'pages', documents.rest.PageViewSet)
router.register(r'courses', catalog.rest.CourseViewSet)
router.register(r'categories', catalog.rest.CategoryViewSet)

docs = router.register(r'documents', documents.rest.DocumentViewSet)
docs.register(
    r'page_set',
    documents.rest.PageViewSet,
    base_name='page-set',
    parents_query_lookups=['document'],
)

urlpatterns = router.urls
