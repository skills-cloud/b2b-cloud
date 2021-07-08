from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

from api import urls as api_urls

urlpatterns = []

app_urlpatterns = [
    path('admin/', admin.site.urls),
    path("autocomplete/", include('django_select2.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    app_urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('api/', include(app_urlpatterns + api_urls.urlpatterns)),
]
