from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/v1/', include('auto_park.urls')),
    path('api/v1/auth/', include('auth_user.urls')),
]
