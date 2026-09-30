from rest_framework.routers import DefaultRouter

from .views import AddressViewSet, ProfileViewSet, UserViewSet


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("profiles", ProfileViewSet, basename="profile")
router.register("addresses", AddressViewSet, basename="address")

urlpatterns = router.urls
