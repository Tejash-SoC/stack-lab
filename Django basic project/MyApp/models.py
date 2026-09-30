from django.db import models
from django.forms import ModelForm
# Create your models here.
class Movie(models.Model):
    Name=models.CharField(max_length=100)
    Rating=models.DecimalField(decimal_places=2,max_digits=10)
    Description=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.Name} - {self.Rating}"

class MovieForm(ModelForm): 
    class Meta:
        model=Movie
        fields="__all__"