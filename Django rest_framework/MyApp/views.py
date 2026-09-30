from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from MyApp.serializers import PersonSerializer
from MyApp.models import Person
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,UpdateAPIView,RetrieveAPIView,DestroyAPIView,CreateAPIView,GenericAPIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from MyApp.pagination import PersonPagination
from rest_framework.mixins import ListModelMixin,CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import django_filters


# Create your views here.
def index(request):
    return HttpResponse('Hello')




#  Function Based Views

@api_view(['GET','POST'])
def getpost(request):
    if(request.method=='GET'):
        d=Person.objects.all()
        ser=PersonSerializer(d,many=True)
        return Response(ser.data)
    elif(request.method=='POST'):
        ser=PersonSerializer(data=request.data,many=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)

@api_view(['GET'])
def content(request):
    d=Person.objects.all()
    serializer=PersonSerializer(d,many=True)
    return Response(serializer.data)
    # return Response(serializer) # -->  it returns a list of json objects 

@api_view(['POST'])
def post_content(request):
    serializer=PersonSerializer(data=request.data,many=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['PUT'])
def upgrade(request,pk):
    p=Person.objects.get(id=pk)
    ser=PersonSerializer(p,data=request.data)
    if ser.is_valid():
        ser.save()
        return Response(ser.data)
    return Response(ser.errors)

@api_view(['DELETE'])
def remove(request,pk):
    p=Person.objects.get(id=pk)
    p.delete()
    return Response('Successfully deleted')


# Class Based Views

class PersonAPI(APIView):
    def get(self,request,pk=None):
            if pk:
                p=Person.objects.get(id=pk)
            else:
                p=Person.objects.all()
            ser=PersonSerializer(p)
            return Response(ser.data)
    def post(self,request):
        ser=PersonSerializer(data=request.data,many=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
    def put(self,request,pk):
        p=Person.objects.get(id=pk)
        ser=PersonSerializer(p,data=request.data)
        if(ser.is_valid()):
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
    def patch(self,request,pk):
        p=Person.objects.get(id=pk)
        ser=PersonSerializer(p,data=request.data)
        if(ser.is_valid()):
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
    def delete(self,request,pk):
        d=Person.objects.get(id=pk)
        d.delete()
        return Response("Successfully deleted")

# Mixins

class Mixins(ListModelMixin,GenericAPIView):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer
    def get(self,request):
        return Response(request.data)



# Generic Views

class ListClass(ListAPIView):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer
class CreateClass(CreateAPIView):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer
class RetriveClass(RetrieveAPIView):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer
class UpdateClass(UpdateAPIView):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer
class DestroyClass(DestroyAPIView):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer

# filter class

class Personfilter(django_filters.FilterSet):
    min_age=django_filters.NumberFilter(field_name='Age',lookup_expr='gte')
    max_age=django_filters.NumberFilter(field_name='Age',lookup_expr='lte')
    Name=django_filters.CharFilter(field_name='Name',lookup_expr='icontains')# startswith, endswith, exact, contains, istartswith, iendswith, iexact, icontains
    Date_created=django_filters.DateFilter(field_name='Date_created',lookup_expr='date')
    

# Model viewset

class ModelView(ModelViewSet):
    queryset=Person.objects.all()
    serializer_class=PersonSerializer
    pagination_class=PersonPagination
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class=Personfilter
    search_fields=['Name','Age']
    ordering_fields=['Name','Age']
    filterset_fields=['Name','Age']

# def get_queryset(self):
#     queryset=Person.objects.all()
#     name=self.request.query_params.get('Name')
#     age=self.request.query_params.get('Age')
#     date=self.request.query_params.get('Date_created')
#     if name:
#         queryset=queryset.filter(Name=name)
#     if age:
#         queryset=queryset.filter(Age=age)
#     return queryset