from rest_framework.routers import APIRootView, DefaultRouter

import catalog.rest
import documents.rest
import notifications.rest
import search.rest
import users.rest
import www.rest


class DochubAPI(APIRootView):
    """
    This is the API of DocHub.

    You are free to use it to crawl DocHub,
    write your own frontend or even make a copy of our documents.

    But please, if you do, respect those rules :

     * To not hit the server too hard. If you degrade the service for other users, we will ban you.
     * Respect the privacy of the users
     * If you scrape and reuse our content, plase credit DocHub and the original uploader.

    This whole API is auth protected.
    To be able to use it without your session cookie,
    use your personal token from <a hre="/api/me">/api/me</a>
    ([doc](http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication))
    """
    pass


class Router(DefaultRouter):
    APIRootView = DochubAPI


router = Router()

router.register(r'users', users.rest.UserViewSet)
router.register(r'courses', catalog.rest.CourseViewSet)
router.register(r'categories', catalog.rest.CategoryViewSet)
router.register(r'documents', documents.rest.DocumentViewSet)
router.register(r'search/courses', search.rest.CourseSearchViewSet, basename="search-courses")
router.register(r'feed', www.rest.FeedViewSet, basename="feed")
router.register(r'me', users.rest.Me, basename="users-me")
router.register(r'notifications', notifications.rest.NotificationsViewSet, basename="notifications")
router.register(r'me/actions', www.rest.SelfFeedViewSet, basename="user-actions")
router.register(r'tree', catalog.rest.Tree, basename="catalog-tree")

urlpatterns = router.urls
