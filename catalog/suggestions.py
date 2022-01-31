import typing

import collections

from django.contrib.contenttypes.models import ContentType

from catalog.models import Course
from users.models import User


def distance(v1: list[bool], v2: list[bool]) -> float:
    absolute_difference = [abs(c1 - c2) for c1, c2 in zip(v1, v2)]
    distance = sum(absolute_difference)
    return distance


def get_users_following_dict() -> dict[int, set[int]]:
    user_following_dict = {}
    for user in User.objects.all():
        user_following_dict[user.id] = {
            course.id for course in user.following_courses()
        }

    return user_following_dict


def suggest(target_user: User, K: int = 15) -> list[tuple[Course, int]]:
    courses = Course.objects.only("id")
    users_following = get_users_following_dict()

    vectors = {}
    for user_id, following in users_following.items():
        vectors[user_id] = [course.id in following for course in courses]

    # If the users is not following any courses, he is not in 'vectors'
    target_vector = vectors.get(target_user.id, [False] * len(courses))

    distances = {
        user_id: distance(target_vector, vector) for user_id, vector in vectors.items()
    }
    non_null_distances = {
        user_id: distance for user_id, distance in distances.items() if distance > 0
    }

    get_score = lambda x: x[1]
    neighbors = sorted(non_null_distances.items(), key=get_score)[:K]

    best_matches: typing.Counter[int] = collections.Counter()
    target_set = users_following[target_user.id]

    for user_id, score in neighbors:
        differences = users_following[user_id] - target_set
        best_matches.update(differences)

    try:
        return [
            (Course.objects.get(id=course_id), hits)
            for course_id, hits in best_matches.most_common()
        ]
    except:
        # Ugly fix to avoid crashing the page if we don't compute the courses
        # TODO log the error (DoesNotExist: Course matching query does not exist.)
        # TODO Scope the except
        return []
