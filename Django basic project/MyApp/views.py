from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from MyApp.pagination import MoviePageNumberPagination
from MyApp.models import Movie
from MyApp.serializer import MovieSerializer


class MovieView(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    page_size=5
    pagination_class=MoviePageNumberPagination


# from django.shortcuts import render, redirect
# from django.http import HttpResponse

# from MyApp.models import MovieForm
# from django.views.generic import DetailView,ListView,UpdateView,CreateView,DeleteView

# class ListClassView(ListView):
#     model=Movie
#     template_name='index.html'
#     context_object_name='x'


# # def home(request):
# #     m=Movie.objects.all()
# #     return render(request,'index.html',context={'x':m})

# class DetailClassView(DetailView):
#     model=Movie
#     template_name='movie.html'
#     context_object_name='x'

# # def movie(request,id):
# #     m=Movie.objects.get(id=id)
# #     return render(request,'movie.html',context={'x':m})

# class CreateClassView(CreateView):
#     model=Movie
#     form_class=MovieForm
#     template_name='addMovie.html'
#     context_object_name='form'
#     success_url='/App/home'

# # def addMovie(request):
# #     if request.method == 'POST':
# #         form=MovieForm(request.POST)
# #         # print(request.POST)
# #         if form.is_valid():
# #             form.save()
# #         return redirect(home)
# #     return render(request,'addMovie.html',context={'form':MovieForm()})

# class UpdateClassView(UpdateView):
#     model=Movie
#     form_class=MovieForm
#     template_name='form.html'
#     context_object_name='form'
#     success_url='/App/home'

# # def editMovie(request,id):
# #     mov=Movie.objects.get(id=id)
# #     form=MovieForm(instance=mov)
# #     if request.method=='POST':
# #         form=MovieForm(request.POST,instance=mov)
# #         if form.is_valid():
# #             form.save()
# #         # return redirect(home)
# #         return redirect(movie,id=id)
# #     return render(request,'form.html',context={'form':form})

# class DeleteClassView(DeleteView):
#     model=Movie
#     # form_class=MovieForm
#     template_name='deleteMovie.html'
#     context_object_name='movie'
#     success_url='/App/home'

# # def deleteMovie(request,id):
# #     mov=Movie.objects.get(id=id)
# #     if request.method=='POST':
# #         mov.delete()
# #         return redirect(home)
# #     return render(request,'deleteMovie.html',context={'movie':mov})


