from django.db import models
class Client(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email= models.EmailField(unique=True)
    phone= models.CharField(max_length=20,blank=True)

    def __str__(self):
        return f"{self.first_name}  {self.last_name}"
# Create your models here.
