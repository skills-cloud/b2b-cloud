from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('organization', views.OrganizationViewSet)
router.register('organization-project', views.OrganizationProjectViewSet)

urlpatterns = []
urlpatterns += router.urls
