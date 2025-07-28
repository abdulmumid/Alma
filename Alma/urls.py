from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, VerifyCodeView, LoginView, BoardViewSet, RequestPasswordResetView, ResetPasswordView, ProductViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/request/', RequestPasswordResetView.as_view()),
    path('password-reset/confirm/', ResetPasswordView.as_view()),
    path('', include(router.urls)),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)