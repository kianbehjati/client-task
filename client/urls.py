from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, qr_code, AuthenticationViewSet, CSVUploadView
from django.urls import path

router = DefaultRouter()
router.register("client", ClientViewSet)
router.register("authentication", AuthenticationViewSet, basename="auth")
urlpatterns = [
    path("qr_code/<int:pk>", qr_code, name="qr_code"),
    path("csv_import", CSVUploadView.as_view(), name="csv_import"),
]
urlpatterns += router.urls
