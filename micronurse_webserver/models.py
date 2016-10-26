from django.db import models

# Create your models here.

ACCOUNT_GENDER_MALE = 'M'
ACCOUNT_GENDER_FEMALE = 'F'
ACCOUNT_TYPE_OLDER = 'O'
ACCOUNT_TYPE_GUARDIAN = 'G'


class Account(models.Model):
    phone_number = models.CharField(max_length=20, primary_key=True, null=False)
    password = models.CharField(max_length=20, null=False)
    nickname = models.CharField(max_length=25, unique=True, null=False)
    gender = models.CharField(max_length=1, choices=(
        (ACCOUNT_GENDER_MALE, 'Male'),
        (ACCOUNT_GENDER_FEMALE, 'Female')
    ), null=False)
    account_type = models.CharField(max_length=1, choices=(
        (ACCOUNT_TYPE_OLDER, 'Older'),
        (ACCOUNT_TYPE_GUARDIAN, 'Guardian')
    ), null=False)
    portrait = models.BinaryField(null=True)
    register_date = models.DateField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'account'


class Guardianship(models.Model):
    older = models.ForeignKey(Account, null=False, related_name='older_id')
    guardian = models.ForeignKey(Account, null=False, related_name='guardian_id')

    class Meta:
        unique_together = ('older', 'guardian')
        db_table = 'guardianship'


class FriendsCircle(models.Model):
    older = models.ForeignKey(Account, null=False, related_name='the_aged_id')
    friend = models.ForeignKey(Account, null=False,related_name='friend_id')

    class Meta:
        unique_together = ('older', 'friend')
        db_table = 'friends_circle'


class HomeAddress(models.Model):
    older = models.ForeignKey(Account, primary_key=True, null=False)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)

    class Meta:
        db_table = 'home_address'


class Sensor(models.Model):
    account = models.ForeignKey(Account, null=False)
    timestamp = models.DateTimeField(null=False)

    class Meta:
        abstract = True
        unique_together = ('account', 'timestamp')


class Thermometer(Sensor):
    name = models.CharField(max_length=30, null=False)
    temperature = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'thermometer'


class InfraredTransducer(Sensor):
    name = models.CharField(max_length=30, null=False)
    warning = models.BooleanField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'infrared_transducer'


class SmokeTransducer(Sensor):
    name = models.CharField(max_length=30, null=False)
    smoke = models.IntegerField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'smoke_transducer'


class Humidometer(Sensor):
    name = models.CharField(max_length=30, null=False)
    humidity = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'humidometer'


class GPS(Sensor):
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'gps'


class FeverThermometer(Sensor):
    temperature = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'fever_thermometer'


class PulseTransducer(Sensor):
    pulse = models.IntegerField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'pulse_transducer'


class Turgoscope(Sensor):
    low_blood_pressure = models.IntegerField(null=False)
    high_blood_pressure = models.IntegerField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'turgoscope'
