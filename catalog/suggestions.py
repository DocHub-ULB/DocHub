from catalog.models import Course
import collections
from django.contrib.contenttypes.models import ContentType
from actstream.models import Follow


def distance(v1, v2):
    absolute_difference = [abs(c1 - c2) for c1, c2 in zip(v1, v2)]
    distance = sum(absolute_difference)
    return distance


def get_users_following_dict():
    course_type = ContentType.objects.get(app_label="catalog", model="course")
    follows = Follow.objects.filter(content_type=course_type).only('user_id', 'object_id')

    following_dict = collections.defaultdict(set)
    for follow in follows:
        following_dict[follow.user_id].add(int(follow.object_id))

    return following_dict


def suggest(target_user, K=15):
    courses = Course.objects.only('id')
    users_following = get_users_following_dict()

    vectors = {}
    for user_id, following in users_following.items():
        vectors[user_id] = [course.id in following for course in courses]

    # If the users is not following any courses, he is not in 'vectors'
    target_vector = vectors.get(target_user.id, [False] * len(courses))

    distances = {user_id: distance(target_vector, vector) for user_id, vector in vectors.items()}
    non_null_distances = {user_id: distance for user_id, distance in distances.items() if distance > 0}

    get_score = lambda x: x[1]
    neighbors = sorted(non_null_distances.items(), key=get_score)[:K]

    best_matches = collections.Counter()
    target_set = users_following[target_user.id]

    for user_id, score in neighbors:
        differences = users_following[user_id] - target_set
        best_matches.update(differences)

    try:
        return [(Course.objects.get(id=course_id), hits) for course_id, hits in best_matches.most_common()]
    except:
        # Ugly fix to avoid crashing the page if we don't compute the courses
        # TODO log the error (DoesNotExist: Course matching query does not exist.)
        # TODO Scope the except
        return []
