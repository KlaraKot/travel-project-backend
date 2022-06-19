from djongo import models
from enum import Enum, unique
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
# models

class lastId(models.Model):
    lastId = models.IntegerField()

class cityRate(models.Model):
    cityName = models.CharField(max_length=200)
    rate = models.IntegerField()
    userId = models.IntegerField()

class City(models.Model):
    cityName = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    description = models.CharField(max_length=700)
    monuments = models.CharField(max_length=400)
    averageRate = models.FloatField()


class Place(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)


class User(AbstractUser):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=200)
    age = models.IntegerField()
    email = models.CharField(max_length=200, unique = True)
    password = models.CharField(max_length=200)
    languageNative = models.CharField(max_length=200)
    languageForeign = models.CharField(max_length=200)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class HistoryRecord(models.Model):
    id = models.IntegerField(primary_key=True)
    actionType = models.IntegerField()
    actionContent = models.IntegerField()
    date = models.DateTimeField()


class HistoryService(models.Model):
    HistoryRecordCount = models.IntegerField()

class weatherChoice(Enum):
    su = "sunny"
    wa = "warm"
    co = "cold"
    mod= "moderately"

class cityType(Enum):
    vil = "village"
    to = "town"
    ci = "city"
    met = "metropolis"



class Survey(models.Model):
    id = models.IntegerField(primary_key=True)
    visitedPlaces = models.CharField(max_length=200)
    preferencePlaces = models.CharField(max_length=200)
    language = models.CharField(max_length=200)
    seaOrMountains = models.CharField(max_length=200)
    companion = models.CharField(max_length = 200)
    wheelchair = models.BooleanField(default=False)
    animals = models.BooleanField(default=False)
    listOfPreferences = models.CharField(max_length=200)
    weather = models.CharField(max_length=200)
    typeOfCity = models.CharField(max_length=200)