from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
  name = models.CharField(max_length=255)

  class Meta():
    ordering = ('name', )
    verbose_name_plural = 'Categories'
  
  def __str__(self):
    return self.name

class Item(models.Model):
  category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
  name = models.CharField(max_length=255)
  image = models.ImageField(upload_to="Item_Images", blank=True, null=True)
  description = models.TextField(blank=True, null=True)
  price = models.FloatField()
  sold = models.BooleanField(default=False)
  creator = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
  creationTime = models.DateTimeField(auto_now_add=True)

  class Meta():
    ordering = ('-creationTime',)

  def __str__(self):
    return self.name
