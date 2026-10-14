from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AuthenticationViewSet, ClientViewSet, CSVUploadView, qr_code

router = DefaultRouter()
router.register("client", ClientViewSet)
router.register("authentication", AuthenticationViewSet, basename="auth")
urlpatterns = [
    path("qr_code/<int:pk>", qr_code, name="qr_code"),
    path("csv_import", CSVUploadView.as_view(), name="csv_import"),
]
urlpatterns += router.urls
