from django.urls import path
import telepathy.views

urlpatterns = [
    path("put/<slug:course_slug>", telepathy.views.new_thread, name="thread_put"),
    path("doc_put/<int:document_id>", telepathy.views.new_thread, name="document_thread_put"),
    path("<int:pk>/reply", telepathy.views.reply_thread, name="thread_reply"),
    path("<int:pk>/", telepathy.views.show_thread, name="thread_show"),
    path("fragment/<int:pk>/", telepathy.views.show_thread_fragment, name="thread_show_fragment"),
    path("<int:pk>/edit", telepathy.views.edit_message, name="edit_message"),
    path("join/<int:pk>", telepathy.views.join_thread, name="join_thread"),
    path("leave/<int:pk>", telepathy.views.leave_thread, name="leave_thread"),
]
