from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth.models import User

class Plan(models.Model):
    plan_id = models.CharField(max_length=12, default='')
    name = models.CharField(max_length=120)
    description = models.TextField()
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(default=1)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    coupon_id = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(max_digits=3, decimal_places=0)
    status = models.BooleanField(default=False)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120, default='')
    last_name = models.CharField(max_length=120, default='')
    country = CountryField(default='')
    contact_no = models.CharField(max_length=20, default='')
    order_id = models.CharField(max_length=240, default='', null=True, blank=True)
    order_TxTime = models.DateTimeField(null=True, blank=True)
    order_Status = models.CharField(max_length=80, null=True, blank=True, default='')
    expiry_date = models.DateTimeField(null=True, blank=True)
    current_plan = models.CharField(max_length=120 , blank=True, null=True, default='')

    def __str__(self):
        return self.first_name