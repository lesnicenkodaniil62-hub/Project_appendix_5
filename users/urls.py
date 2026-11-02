from django.urls import URLPattern, URLResolver, path

from .views import UserUpdateAPIView

urlpatterns: list[URLPattern | URLResolver] = [
    path("users/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
]
