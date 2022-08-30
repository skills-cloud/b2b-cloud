from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

from api.handlers.acc import views as acc_views


urlpatterns = []

app_urlpatterns = [
    path('admin/', admin.site.urls),
    path("autocomplete/", include('django_select2.urls')),
    path('nested_admin/', include('nested_admin.urls')),
]

api_v1 = [
    path('docs/', include('api.schema.urls')),
    path('acc/', include([
        path('whoami/set-photo/', acc_views.WhoAmISetPhotoView.as_view()),
        path('whoami/', acc_views.WhoAmIView.as_view()),
        path('login/', acc_views.LoginView.as_view()),
        path('logout/', acc_views.LogoutView.as_view()),
        path('set-timezone/', acc_views.SetTimezone.as_view()),
    ])),
    path('main/', include('api.handlers.main.urls')),
    path('dictionary/', include('api.handlers.dictionary.urls')),
    path('cv/', include('api.handlers.cv.urls')),
]


if settings.DEBUG:
    import debug_toolbar

    app_urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('api/', include(app_urlpatterns + api_v1)),
    path('i18n/', include('django.conf.urls.i18n')),
]
