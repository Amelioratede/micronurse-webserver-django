from django.db import models

# Create your models here.


class Account(models.Model):
    phone_number = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=20)
    nickname = models.CharField(max_length=25)
    gender = models.CharField(max_length=1, choices=(
        ('M', 'Male'),
        ('F', 'Female')
    ))
    account_type = models.CharField(max_length=1, choices=(
        ('O', 'Older'),
        ('G', 'Guardian')
    ))
    portrait = models.BinaryField(null=True)
    register_date = models.DateField(auto_now_add=True)


class Sensor(models.Model):
    account = models.ForeignKey(Account)
    timestamp = models.DateTimeField()
    name = models.CharField(max_length=30)

    class Meta:
        abstract = True
        ordering = ['-timestamp']
        unique_together = ('account', 'name', 'timestamp')


class Thermometer(Sensor):
    temperature = models.FloatField()


class Humidometer(Sensor):
    humidity = models.FloatField()


class GPS(Sensor):
    longitude = models.FloatField()
    latitude = models.FloatField()

