import time
from django.db import models

# Create your models here.
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class Account(models.Model):
    phone_number = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=20)
    nickname = models.CharField(max_length=25)
    gender = models.CharField(max_length=1, choices=(
        ('M', 'Male'),
        ('F', 'Female')
    ))
    portrait = models.ImageField(null=True)
    birth = models.DateField(null=True)
    register_date = models.DateField(auto_now_add=True)