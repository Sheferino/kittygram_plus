from django.urls import include, path

from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from cats.views import CatViewSet, OwnerViewSet, CatAddList


router = DefaultRouter()
router.register('cats', CatViewSet)
router.register('owners', OwnerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cats_list/', CatAddList.as_view()),
    # маршрут получения токена
    path('api-token-auth/', views.obtain_auth_token),
]
