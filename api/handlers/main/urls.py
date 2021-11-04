from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('organization', views.OrganizationViewSet)
router.register('organization-project', views.OrganizationProjectViewSet)
router.register('organization-project-card-item-template', views.OrganizationProjectCardItemTemplateViewSet)
router.register('organization-project-card-item', views.OrganizationProjectCardItemViewSet)
router.register('fun-point-type-difficulty-level', views.FunPointTypeDifficultyLevelViewSet)
router.register('fun-point-type-position-labor-estimate', views.FunPointTypePositionLaborEstimateViewSet)
router.register('fun-point-type', views.FunPointTypeViewSet)
router.register('module', views.ModuleViewSet)
router.register('module-fun-point', views.ModuleFunPointViewSet)
router.register('module-position-labor-estimate', views.ModulePositionLaborEstimateViewSet)
router.register('request-type', views.RequestTypeViewSet)
router.register('request', views.RequestViewSet)
router.register('request-requirement', views.RequestRequirementViewSet)
router.register('time-sheet-row', views.TimeSheetRowViewSet)

urlpatterns = []
urlpatterns += router.urls
