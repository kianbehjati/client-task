from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, qr_code, AuthenticationViewSet
from django.urls import path

router = DefaultRouter()
router.register('client', ClientViewSet)
router.register('authentication', AuthenticationViewSet, basename="auth")
urlpatterns = [
    path('qr_code/<int:pk>', qr_code, name='qr_code')
]
urlpatterns += router.urls