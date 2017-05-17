from django.db import models

# Create your models here.

ACCOUNT_GENDER_MALE = 'M'
ACCOUNT_GENDER_FEMALE = 'F'
ACCOUNT_TYPE_OLDER = 'O'
ACCOUNT_TYPE_GUARDIAN = 'G'


class Account(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    phone_number = models.CharField(max_length=20, unique=True, null=False)
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
    address = models.CharField(null=False, max_length=80)

    class Meta:
        db_table = 'home_address'


class Sensor(models.Model):
    account = models.ForeignKey(Account, null=False)
    timestamp = models.DateTimeField(null=False)

    class Meta:
        abstract = True
        unique_together = ('account', 'timestamp')
        ordering = ['-timestamp']


class SensorInstance(models.Model):
    account = models.ForeignKey(Account, null=False)
    sensor_type = models.CharField(null=False, max_length=20)
    name = models.CharField(null=False, max_length=20)

    class Meta:
        db_table = 'sensor_instance'
        unique_together = ('account', 'sensor_type', 'name')


class FamilySensor(models.Model):
    instance = models.ForeignKey(SensorInstance, null=False)
    timestamp = models.DateTimeField(null=False)

    class Meta:
        abstract = True
        unique_together = ('instance', 'timestamp')
        ordering = ['-timestamp']


class Thermometer(FamilySensor):
    sensor_type = 'thermometer'
    temperature = models.FloatField(null=False)

    class Meta(FamilySensor.Meta):
        db_table = 'thermometer'


class InfraredTransducer(FamilySensor):
    sensor_type = 'infrared_transducer'
    warning = models.BooleanField(null=False)

    class Meta(FamilySensor.Meta):
        db_table = 'infrared_transducer'


class SmokeTransducer(FamilySensor):
    sensor_type = 'smoke_transducer'
    smoke = models.IntegerField(null=False)

    class Meta(FamilySensor.Meta):
        db_table = 'smoke_transducer'


class Humidometer(FamilySensor):
    sensor_type = 'humidometer'
    humidity = models.FloatField(null=False)

    class Meta(FamilySensor.Meta):
        db_table = 'humidometer'


class GPS(Sensor):
    sensor_type = 'gps'
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)
    address = models.CharField(null=False, max_length=80)

    class Meta(Sensor.Meta):
        db_table = 'gps'


class FeverThermometer(Sensor):
    sensor_type = 'fever_thermometer'
    temperature = models.FloatField(null=False)

    class Meta(Sensor.Meta):
        db_table = 'fever_thermometer'


class PulseTransducer(Sensor):
    sensor_type = 'pulse_transducer'
    pulse = models.IntegerField(null=False)

    class Meta(Sensor.Meta):
        db_table = 'pulse_transducer'


class SensorConfig(models.Model):
    user = models.OneToOneField(Account, primary_key=True)
    infrared_enabled = models.BooleanField(null=False, default=True)
