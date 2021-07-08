from django.conf import settings
from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from api.handlers import schema as views_schema
from api.handlers.acc import views as views_acc
from api.handlers.main import views as views_main

app_name = 'api'


class RouterMain(routers.DefaultRouter):
    pass


api_urlpatterns_acc = [
    path('whoami/set-photo/', views_acc.WhoAmISetPhotoView.as_view()),
    path('whoami/', views_acc.WhoAmIView.as_view()),
    path('login/', views_acc.LoginView.as_view()),
    path('logout/', views_acc.LogoutView.as_view()),
    path('set-timezone/', views_acc.SetTimezone.as_view()),
    # path('acc/password/change/', views_acc.PasswordChangeView.as_view(), name='rest_password_change'),
    # path('acc/password/reset/confirm/', views_acc.PasswordResetConfirmView.as_view(), name='rest_password_confirm'),
    # path('acc/password/reset/', views_acc.PasswordResetView.as_view(), name='rest_password'),
    # path('acc/registration/', views_acc.RegistrationView.as_view(), name='registration'),
]

api_urlpatterns_doc = [
    path('swagger/', views_schema.SchemaView.with_ui('swagger', cache_timeout=0)),
    path('redoc/', views_schema.SchemaView.with_ui('redoc', cache_timeout=0)),
]

router_main = RouterMain()

api_urlpatterns_main = [
]
api_urlpatterns_main += router_main.urls

urlpatterns = [
    path('acc/', include(api_urlpatterns_acc)),
    path('docs/', include(api_urlpatterns_doc)),
    path('main/', include(api_urlpatterns_main)),
]
