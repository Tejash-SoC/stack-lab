from rest_framework.response import Response
from django.urls import path
from .views import index
from MyApp import views
from MyApp.views import PersonAPI,ListClass,CreateClass,UpdateClass,RetriveClass,DestroyClass,ModelView
from rest_framework.routers import DefaultRouter
# ModelViewSet
router = DefaultRouter()
router.register('people',ModelView,basename='people')
urlpatterns = [

    # Function Based Views
    path('index/',index,name='index'),
    path('get/',views.content),
    path('post/',views.post_content),
    path('getpost/',views.getpost),
    path('upgrade/<int:pk>',views.upgrade),
    path('delete/<int:pk>/',views.remove),

    # Class Based Views
    path('person/<int:pk>/',PersonAPI.as_view()),

    # Mixins
    path('getmixin/',views.Mixins.as_view()),

    # Generic Views
    path('list/',ListClass.as_view()),
    path('create/',CreateClass.as_view()),
    path('retrive/<int:pk>/',RetriveClass.as_view()),
    path('update/<int:pk>/',UpdateClass.as_view()),
    path('destroy/<int:pk>/',DestroyClass.as_view()),
     

]

urlpatterns+=router.urls
