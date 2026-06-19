from django.urls import path

from . import views


urlpatterns = [
    path("", views.review_list),
    path("orders/<int:order_id>/", views.create_review),
    path("orders/<int:order_id>/detail/", views.review_detail),
    path("orders/<int:order_id>/history/", views.review_history),
]
