from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('organization', views.OrganizationViewSet)
router.register('organization-project', views.OrganizationProjectViewSet)
router.register('project', views.ProjectViewSet)
router.register('request-type', views.RequestTypeViewSet)
router.register('request', views.RequestViewSet)
router.register('request-requirement', views.RequestRequirementViewSet)

urlpatterns = []
urlpatterns += router.urls
