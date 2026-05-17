from django.db import connection, models
from django.utils import timezone


class Metric(models.TextChoices):
    DOCUMENT_VIEW = "document_view", "Vues de documents"
    DOCUMENT_DOWNLOAD = "document_download", "Téléchargements"
    SEARCH_QUERY = "search_query", "Recherches"
    COURSE_PAGE_VIEW = "course_page_view", "Vues de cours"
    LOGIN_SUCCESS = "login_success", "Connexions"
    COURSE_FOLLOW = "course_follow", "Cours suivis"
    COURSE_UNFOLLOW = "course_unfollow", "Cours dé-suivis"
    DOCUMENT_EDIT = "document_edit", "Éditions de documents"
    STATS_VIEW = "stats_view", "Vues de la page stats"
    MODERATION_LOG_VIEW = "moderation_log_view", "Vues du log de modération"
    MODERATION_TREE_VIEW = (
        "moderation_tree_view",
        "Vues de l'arbre de modération",
    )
    UPLOAD_SUBMIT = "upload_submit", "Soumissions d'upload"
    DOCUMENT_REUPLOAD = "document_reupload", "Réuploads de documents"
    MY_COURSES_VIEW = "my_courses_view", 'Vues de "Mes cours"'
    MODERATION_PROFILE_VIEW = (
        "moderation_profile_view",
        "Vues de profils de modérateur·trices",
    )
    DOCUMENT_HISTORY_VIEW = (
        "document_history_view",
        "Vues d'historique de documents",
    )
    MODERATION_ABOUT_VIEW = (
        "moderation_about_view",
        "Vues de la page modération (utilisateurs)",
    )
    MODERATION_ABOUT_VIEW_MOD = (
        "moderation_about_view_mod",
        "Vues de la page modération (modérateur·trices)",
    )
    FINDER_VIEW = "finder_view", "Vues du finder"
    FINDER_VIEW_DEEP = "finder_view_deep", "Vues du finder (profondeur ≥ 3)"
    MODERATION_MANAGE_VIEW = (
        "moderation_manage_view",
        "Vues de la gestion des modérateur·trices",
    )


class DailyStat(models.Model):
    """Aggregate counter — one row per (date, metric name)."""

    date = models.DateField()
    name = models.CharField(max_length=64, choices=Metric)
    value = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "name"], name="unique_dailystat"),
        ]
        indexes = [
            models.Index(fields=["name", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.date} {self.name}={self.value}"

    @classmethod
    def track(cls, metric: Metric) -> None:
        """Atomically bump today's counter for `metric` by 1.

        Uses ON CONFLICT DO UPDATE — one statement, true atomicity. Works on
        Postgres and SQLite.
        """
        with connection.cursor() as cursor:
            cursor.execute(_UPSERT_SQL, [timezone.localdate(), metric])


# quote_name() is the Django-blessed way to interpolate an identifier into raw
# SQL. The fstring runs once at module load; cursor.execute() only ever sees a
# constant SQL string + parameters.
_TABLE = connection.ops.quote_name(DailyStat._meta.db_table)
_UPSERT_SQL = (
    f"INSERT INTO {_TABLE} (date, name, value) VALUES (%s, %s, 1) "
    f"ON CONFLICT (date, name) DO UPDATE SET value = {_TABLE}.value + 1"
)
