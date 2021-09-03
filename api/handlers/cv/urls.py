from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('cv', views.CvViewSet)
router.register('contact', views.CvContactViewSet)
router.register('time-slot', views.CvTimeSlotViewSet)
router.register('position', views.CvPositionViewSet)
router.register('career', views.CvCareerViewSet)
router.register('project', views.CvProjectViewSet)
router.register('education', views.CvEducationViewSet)
router.register('certificate', views.CvCertificateViewSet)

urlpatterns = []
urlpatterns += router.urls
