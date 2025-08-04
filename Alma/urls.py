from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'products', ProductViewSet)
router.register(r'stories', StoryViewSet)
router.register(r'cart', CartItemViewSet)
router.register(r'bonuses', UserBonusViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/request/', RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', ResetPasswordView.as_view(), name='password_reset_confirm'),
    path('', include(router.urls)),
    path('nearest-store/', NearestStoreView.as_view(), name='nearest_store'),
    path('check-price/', CheckPriceView.as_view(), name='check_price'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
