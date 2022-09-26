from rest_framework import routers

from django.urls import path, include

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('organization', views.OrganizationViewSet)
router.register('organization-customer', views.OrganizationCustomerViewSet)
router.register('organization-contractor', views.OrganizationContractorViewSet)
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

urlpatterns = [
    path('partners/', include([
        path('<int:pk>/', views.PartnerDetailView.as_view()),
        path('', views.PartnerDetailView.as_view())
    ])),
    path('partner-networks/', include([
        path('<int:pk>/', views.PartnerNetworkDetailView.as_view()),
        path('', views.GetOrCreatePartnerNetworkView.as_view()),
    ]))

]
urlpatterns += router.urls
