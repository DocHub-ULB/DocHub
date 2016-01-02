from users.models import User
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
    follows = Follow.objects\
        .filter(content_type=course_type)\
        .select_related('user')\
        .prefetch_related('follow_object')

    following_dict = collections.defaultdict(set)
    for follow in follows:
        following_dict[follow.user.netid].add(follow.follow_object)

    return following_dict


def suggest(target_user, K=15):
    courses = Course.objects.all()
    users = {user.netid: user for user in User.objects.all()}
    users_following = get_users_following_dict()

    vectors = {}
    for netid, user in users.items():
        following = users_following[netid]
        vectors[netid] = [course in following for course in courses]

    target_vector = vectors[target_user.netid]

    distances = {netid: distance(target_vector, vector) for netid, vector in vectors.items()}
    non_null_distances = {netid: distance for netid, distance in distances.items() if distance > 0}

    get_score = lambda x: x[1]
    neighbors = sorted(non_null_distances.items(), key=get_score)[:K]

    best_matches = collections.Counter()
    target_set = users_following[target_user.netid]

    for netid, score in neighbors:
        differences = users_following[netid] - target_set
        best_matches.update(differences)

    return best_matches
