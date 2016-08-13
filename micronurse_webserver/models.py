from django.db import models

# Create your models here.


class Account(models.Model):
    phone_number = models.CharField(max_length=20, primary_key=True, null=False)
    password = models.CharField(max_length=20, null=False)
    nickname = models.CharField(max_length=25, unique=True, null=False)
    gender = models.CharField(max_length=1, choices=(
        ('M', 'Male'),
        ('F', 'Female')
    ), null=False)
    account_type = models.CharField(max_length=1, choices=(
        ('O', 'Older'),
        ('G', 'Guardian')
    ), null=False)
    portrait = models.BinaryField(null=True)
    register_date = models.DateField(auto_now_add=True, null=False)


class Sensor(models.Model):
    account = models.ForeignKey(Account, null=False)
    timestamp = models.DateTimeField(null=False)

    class Meta:
        abstract = True
        ordering = ['-timestamp']
        unique_together = ('account', 'timestamp')


class Thermometer(Sensor):
    name = models.CharField(max_length=30, null=False)
    temperature = models.FloatField(null=False)


class InfraredTransducer(Sensor):
    name = models.CharField(max_length=30, null=False)
    warning = models.BooleanField(null=False)


class SmokeTransducer(Sensor):
    name = models.CharField(max_length=30, null=False)
    smoke = models.IntegerField(null=False)


class Humidometer(Sensor):
    name = models.CharField(max_length=30, null=False)
    humidity = models.FloatField(null=False)


class GPS(Sensor):
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)


class FeverThermometer(Sensor):
    temperature = models.FloatField(null=False)


class PulseTransducer(Sensor):
    pulse = models.IntegerField(null=False)


class Turgoscope(Sensor):
    low_blood_pressure = models.IntegerField(null=False)
    high_blood_pressure = models.IntegerField(null=False)
