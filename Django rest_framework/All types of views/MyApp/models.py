from django.db import models
# Create your models here.
class Person(models.Model):
    Name=models.CharField(max_length=100)
    Age=models.DecimalField(decimal_places=2,max_digits=10)
    Date_created=models.DateField(auto_now=True)
    def __str__(self) -> str:
        return self.Name

 