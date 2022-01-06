from django.urls import path
from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


urlpatterns = [
    path('whoami/set-photo/', views.WhoAmISetPhotoView.as_view()),
    path('whoami/', views.WhoAmIView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('set-timezone/', views.SetTimezone.as_view()),
    # path('acc/password/change/', views.PasswordChangeView.as_view(), name='rest_password_change'),
    # path('acc/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='rest_password_confirm'),
    # path('acc/password/reset/', views.PasswordResetView.as_view(), name='rest_password'),
    # path('acc/registration/', views.RegistrationView.as_view(), name='registration'),
]

router = Router()
router.register('user-manage', views.UserManageViewSet)


urlpatterns += router.urls
