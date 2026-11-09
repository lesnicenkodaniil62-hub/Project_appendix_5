from django.urls import URLPattern, URLResolver, path
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentListAPIView,
    UserProfileAPIView,
    UserRegisterAPIView,
    UserUpdateAPIView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

urlpatterns: list[URLPattern | URLResolver] = [
    path("register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("users/<int:pk>/profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path("users/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
]

urlpatterns += router.urls
