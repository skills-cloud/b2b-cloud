from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('type-of-employment', views.TypeOfEmploymentViewSet)
router.register('country', views.CountryViewSet)
router.register('city', views.CityViewSet)
router.register('citizenship', views.CitizenshipViewSet)
router.register('contact-type', views.ContactTypeViewSet)
router.register('education-place', views.EducationPlaceViewSet)
router.register('education-specialty', views.EducationSpecialtyViewSet)
router.register('education-graduate', views.EducationGraduateViewSet)
router.register('position', views.PositionViewSet)
router.register('physical-limitation', views.PhysicalLimitationViewSet)
router.register('industry-sector', views.IndustrySectorViewSet)
router.register('competence-tree', views.CompetenceTreeViewSet)
router.register('competence', views.CompetenceViewSet)

urlpatterns = []
urlpatterns += router.urls
