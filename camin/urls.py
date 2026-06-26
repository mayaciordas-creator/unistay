"""
Configurarea URL-urilor principale pentru proiectul Django.

Acest fișier conectează:
- URL-urile din aplicația 'cazare'
- Panoul de administrare Django
- Paginile de autentificare (login/logout)
- Servirea fișierelor media în dezvoltare
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from cazare import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    path('', include('cazare.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
