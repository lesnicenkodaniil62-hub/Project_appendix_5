from django.urls import URLPattern, URLResolver, path

from .views import PaymentListAPIView, UserProfileAPIView, UserUpdateAPIView

urlpatterns: list[URLPattern | URLResolver] = [
    path("users/<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("users/<int:pk>/profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
]
