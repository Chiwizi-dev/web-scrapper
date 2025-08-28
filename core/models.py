from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from datetime import datetime


User = get_user_model()

# Create your models here.


# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     price = models.CharField(max_length=50)
#     image_url = models.URLField(blank=True, null=True)
#     scraped_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


class Author(models.Model):
    author = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.author)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.author


class Tag(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        Author, on_delete=models.SET_NULL, related_name="quotes", null=True
    )
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'"{self.text[:50]}..." by {self.author.author}'
