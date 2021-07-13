from django.conf.urls import include
from django.urls import path

app_name = 'api'

urlpatterns = [
    path('docs/', include('api.schema.urls')),
    path('acc/', include('api.handlers.acc.urls')),
    path('main/', include('api.handlers.main.urls')),
    path('dictionary/', include('api.handlers.dictionary.urls')),
    path('cv/', include('api.handlers.cv.urls')),
]
