from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('mainsite.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('oauth/', include('oauth.urls')),
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(template_name='oauth/logout.html'), name='logout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
