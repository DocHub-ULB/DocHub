from django.db import migrations


def delete_numeric_netid_users(apps, schema_editor):
    User = apps.get_model("users", "User")
    Document = apps.get_model("documents", "Document")
    Course = apps.get_model("catalog", "Course")

    numeric_users = User.objects.filter(netid__regex=r"^\d+$")
    numeric_user_ids = set(numeric_users.values_list("id", flat=True))

    if not numeric_user_ids:
        return

    # Safety check: we expect ~64, more than 100 would be suspicious
    if len(numeric_user_ids) > 100:
        raise RuntimeError(
            f"Expected ~64 numeric-netid users, found {len(numeric_user_ids)}"
        )

    # Safety check: none of these users should have documents
    doc_count = Document.objects.filter(user__in=numeric_user_ids).count()
    if doc_count:
        raise RuntimeError(
            f"Cannot delete numeric-netid users: {doc_count} documents would be lost"
        )

    # Transfer course follows from duplicate numeric-netid users to their
    # original account (matched by email local part) where possible.
    for user in numeric_users.iterator():
        courses = Course.objects.filter(followed_by=user)
        if not courses.exists():
            continue

        local_part = user.email.split("@")[0].lower()
        original = (
            User.objects.filter(email__istartswith=local_part + "@")
            .exclude(netid__regex=r"^\d+$")
            .exclude(id=user.id)
            .first()
        )

        if original:
            for course in courses:
                course.followed_by.add(original)

    deleted_count, _ = numeric_users.delete()
    print(f"\n  Deleted {deleted_count} users with numeric netids")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0009_remove_legacy_tables"),
    ]

    operations = [
        migrations.RunPython(delete_numeric_netid_users, migrations.RunPython.noop),
    ]
