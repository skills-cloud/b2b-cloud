from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic import RedirectView

from api import urls as api_urls

urlpatterns = []

app_urlpatterns = [
    path('admin/', admin.site.urls),
    path('autocomplete/', include('django_select2.urls')),
    path('nested_admin/', include('nested_admin.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    app_urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DJANGO_SILK_ENABLED:
    app_urlpatterns.append(path('silk/', include('silk.urls', namespace='silk')))

urlpatterns += [
    path('favicon.ico', RedirectView.as_view(url=f'{settings.STATIC_URL}img/reset.png', permanent=True)),
    path('api/', include(app_urlpatterns + api_urls.urlpatterns)),
]
