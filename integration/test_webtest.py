import django_webtest
import pytest
from django.urls import reverse
from webtest import Upload

from catalog.models import CatalogEdition, Category, Course
from documents.models import Document
from tags.models import Tag
from users.models import User

pytestmark = [pytest.mark.django_db, pytest.mark.webtest]


@pytest.fixture
def app():
    wtm = django_webtest.WebTestMixin()
    wtm._patch_settings()
    yield django_webtest.DjangoTestApp()
    wtm._unpatch_settings()


@pytest.fixture
def user():
    return User.objects.create_user(
        netid="nimarcha", email="lol@lol.be", first_name="Nikita", last_name="Marchant"
    )


@pytest.fixture
def tags():
    return [Tag.objects.create(name="my tag"), Tag.objects.create(name="my other tag")]


@pytest.fixture
def edition():
    return CatalogEdition.objects.create(
        key="test",
        status=CatalogEdition.Status.ACTIVE,
    )


@pytest.fixture
def tree(edition):
    root = Category.objects.create(name="ULB", edition=edition)
    science = Category.objects.create(name="science", edition=edition)
    science.parents.add(root)
    swag = Course.objects.create(
        name="Optimization of algorithmical SWAG", slug="swag-h-042"
    )
    swag.categories.add(science)

    return root


def test_name_in_page(app, user, edition):
    Category.objects.create(
        name="ULB",
        slug="root",
        edition=edition,
    )

    index = app.get("/", user=user.netid)
    assert user.initials() in index


@pytest.mark.skip(reason="HTML changed too much in recent version")
def test_follow(app, user, tree):
    index = app.get("/", user=user.netid)
    catalog = index.click(href=reverse("catalog:show_courses"), index=0)
    category = catalog.click(description="science")
    course = category.click(description=lambda x: "Optimization" in x)
    course = course.click(
        # description="S'abonner",
        href=reverse("join_course", args=("swag-h-042",)),
    ).follow()

    assert "Se désabonner" in course

    index = app.get("/", user=user.netid)
    assert "swag-h-042" in index

    course = course.click(
        href=reverse("catalog:leave_course", args=("swag-h-042",)),
    ).follow()

    index = app.get("/", user=user.netid)
    assert "swag-h-042" not in index


@pytest.mark.skip(reason="HTML changed too much in recent version")
def test_follow_from_category(app, user, tree):
    index = app.get("/", user=user.netid)
    catalog = index.click(href=reverse("catalog:show_courses"), index=0)
    category = catalog.click(description="science")
    category = category.click(description=lambda x: "swag-h-042" in x).follow()
    course = category.click(description=lambda x: x.startswith("Optimization"))
    assert "Se désabonner" in course


def test_upload_picker_lists_followed_courses(app, user):
    """The global "Partager" flow lands on a picker that shortcuts followed
    courses straight to their upload form (uploads are course-scoped)."""
    course = Course.objects.create(name="Algo SWAG", slug="swag-h-042")
    course.followed_by.add(user)

    picker = app.get(reverse("document_upload"), user=user.netid)

    assert "Dans quel cours veux-tu partager" in picker
    assert reverse("document_put", args=[course.slug]) in picker


def test_course_search_target_upload_links_to_upload(app, user):
    """?target=upload makes course results point at the upload form instead of
    the course page, so the picker's search deposits documents directly."""
    course = Course.objects.create(name="Algo SWAG", slug="swag-h-042")

    results = app.get("/search/courses/?target=upload&q=swag", user=user.netid)
    assert reverse("document_put", args=[course.slug]) in results

    # The plain navbar search stays pointed at the course page.
    results = app.get("/search/courses/?q=swag", user=user.netid)
    assert reverse("catalog:course_show", args=[course.slug]) in results


# @mock.patch.object(Document, 'add_to_queue')
@pytest.mark.skip(reason="HTML changed too much in recent version")
def test_simple_upload(app, user, tree, tags):
    course = app.get(
        reverse("catalog:course_show", args=("swag-h-042",)), user=user.netid
    )
    put = course.click(description="Uploader un document")
    form = next(x for x in put.forms.values() if x.id == "document-upload")
    form["file"] = Upload("documents/tests/files/3pages.pdf")
    form["tags"].select_multiple(texts=["my tag"])
    response = form.submit()
    course = response.follow()

    assert Document.objects.count() == 1
