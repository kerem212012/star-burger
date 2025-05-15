from django.db import models
from django.utils import timezone


class Location(models.Model):
    address = models.CharField(verbose_name="Адрес",max_length=200,db_index=True,unique=True)
    lat = models.FloatField(verbose_name="Широта",null=True,blank=True)
    lon = models.FloatField(verbose_name="Долгота",null=True,blank=True)
    query_data = models.DateField(verbose_name="Дата запроса",db_index=True,default=timezone.now)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локация'
