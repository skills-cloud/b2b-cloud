from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('organization', views.OrganizationViewSet)
router.register('organization-project', views.OrganizationProjectViewSet)
router.register('organization-project-card-item-template', views.OrganizationProjectCardItemTemplateViewSet)
router.register('organization-project-card-item', views.OrganizationProjectCardItemViewSet)
router.register('project', views.ProjectViewSet)
router.register('request-type', views.RequestTypeViewSet)
router.register('request', views.RequestViewSet)
router.register('request-requirement', views.RequestRequirementViewSet)
router.register('time-sheet-row', views.TimeSheetRowViewSet)

urlpatterns = []
urlpatterns += router.urls
