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


class Friendship(models.Model):
    older = models.ForeignKey(Account, null=False, related_name='friendship_older_id')
    friend = models.ForeignKey(Account, null=False, related_name='friendship_friend_id')

    class Meta:
        unique_together = ('older', 'friend')
        db_table = 'friendship'


class FriendMoment(models.Model):
    older = models.ForeignKey(Account, null=False)
    timestamp = models.DateTimeField(null=False)
    text_content = models.TextField(null=False)

    class Meta:
        db_table = 'friend_moment'
        unique_together = ('older', 'timestamp')
        ordering = ['-timestamp']


class HomeAddress(models.Model):
    older = models.OneToOneField(Account, primary_key=True)
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
    sensor_type = 'thermometer'
    name = models.CharField(max_length=30, null=False)
    temperature = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'thermometer'


class InfraredTransducer(Sensor):
    sensor_type = 'infrared_transducer'
    name = models.CharField(max_length=30, null=False)
    warning = models.BooleanField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'infrared_transducer'


class SmokeTransducer(Sensor):
    sensor_type = 'smoke_transducer'
    name = models.CharField(max_length=30, null=False)
    smoke = models.IntegerField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'smoke_transducer'


class Humidometer(Sensor):
    sensor_type = 'humidometer'
    name = models.CharField(max_length=30, null=False)
    humidity = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'humidometer'


class GPS(Sensor):
    sensor_type = 'gps'
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'gps'


class FeverThermometer(Sensor):
    sensor_type = 'fever_thermometer'
    temperature = models.FloatField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'fever_thermometer'


class PulseTransducer(Sensor):
    sensor_type = 'pulse_transducer'
    pulse = models.IntegerField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'pulse_transducer'


class Turgoscope(Sensor):
    sensor_type = 'turgoscope'
    low_blood_pressure = models.IntegerField(null=False)
    high_blood_pressure = models.IntegerField(null=False)

    class Meta:
        ordering = ['-timestamp']
        db_table = 'turgoscope'
