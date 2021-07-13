from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('cv', views.CvViewSet)
router.register('contact', views.CvContactViewSet)
router.register('time-slot', views.CvTimeSlotViewSet)

urlpatterns = []
urlpatterns += router.urls
