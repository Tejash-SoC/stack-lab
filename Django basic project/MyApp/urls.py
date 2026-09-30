from django.urls import path
from rest_framework.routers import DefaultRouter

from MyApp import views
from MyApp.views import MovieView


# urlpatterns = [
#     path('home/',views.ListClassView.as_view(),name='home'),
#     path('movie/<int:pk>',views.DetailClassView.as_view(),name='movie'),
#     path('addMovie',views.CreateClassView.as_view(),name='addMovie'),
#     path('editMovie/<int:pk>',views.UpdateClassView.as_view(),name='editMovie'),
#     path('deleteMovie/<int:pk>',views.DeleteClassView.as_view(),name='deleteMovie')
# ]
  
# urlpatterns = []
router = DefaultRouter()
router.register('movie',MovieView,basename='movie')

urlpatterns = []

urlpatterns += router.urls
