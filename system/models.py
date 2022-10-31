from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class Driver(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, default=None, null=True, blank=True)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=60, blank=True, null=True)
    id_number = models.IntegerField(blank=True, null=True)

    # profile_pic = models.ImageField(upload_to='employee_pics/',
    #                                 blank=True)
    phone_number = models.CharField(max_length=70, blank=True)

    def __str__(self):
        return self.user.username

    # @property
    # def profile_pic_url(self):
    #     if self.profile_pic and hasattr(self.profile_pic, 'url'):
    #         return self.profile_pic.url
    #     else:
    #         return "/media/default.png"

    def save_driver(self):
        self.save()

    def update_driver(self, using=None, fields=None, **kwargs):
        if fields is not None:
            fields = set(fields)
            deferred_fields = self.get_deferred_fields()
            if fields.intersection(deferred_fields):
                fields = fields.union(deferred_fields)
        super().refresh_from_db(using, fields, **kwargs)

    def delete_driver(self):
        self.delete()

    def create_driver_profile(sender, **kwargs):
        if kwargs['created']:
            driver_profile = Driver.objects.create(
                user=kwargs['instance'])

    post_save.connect(create_driver_profile, sender=User)


def uploaded_location(instance, filename):
    return ("%s/%s") %(instance.car_name,filename)

class Car(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to=uploaded_location,null=True, blank=True, width_field="width_field", height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    car_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    num_of_seats = models.IntegerField()
    cost_par_day = models.CharField(max_length=50)
    content = models.TextField()
    like = models.IntegerField(default=0)

    def __str__(self):
        return self.car_name

    def get_absolute_url(self):
        return "/car/%s/" % (self.id)

class Order(models.Model):
    car_name = models.ForeignKey(Car, on_delete=models.CASCADE, blank=True, null=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, blank=True, null=True)
    cell_no = models.CharField(max_length=15)
    address = models.TextField()
    date = models.DateTimeField()
    to = models.DateTimeField()

    def __str__(self):
        return self.car_name

    def get_absolute_url(self):
        return "/car/detail/%s/" % (self.id)

class PrivateMsg(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()