from django.db import models
from django.conf import  settings
from django.db.models import  Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from model_utils import  Choices
from multiselectfield import MultiSelectField


# Create your models here.

CATEGORY_CHOICES = (
    ('rent', 'rent'),
    ('sale', 'sale'),
    
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)



AMENITY_CHOICES = (
    ('balcony', 'balcony'),
    ('outdoor_kitchen','outdoor_kitchen'),
    ('cable_tv','cable_tv'),
    ('tennis_court','tennis_court'),
    ('internet','internet'),
    ('deck','deck'),
    ('parking','parking'),
    ('sun_room','sun_room'),
    ('concrete_flooring','concrete_flooring')


)

ROOM_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('more than 10', 'more than 10'),
)



class Property(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=10)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image1 = models.ImageField()
    video = models.FileField()
    country = CountryField(multiple=False)
    amenities = MultiSelectField(choices=AMENITY_CHOICES, max_length=30)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })





# class Amenitiy(models.Model):
#     property = models.ForeignKey(Property, on_delete=models.CASCADE)
#     balcony = models.BooleanField(default=False)
#     outdoor_kitchen = models.BooleanField(default=False)
#     cable_tv = models.BooleanField(default=False)
#     tennis_court = models.BooleanField(default=False)
#     internet = models.BooleanField(default=False)
#     deck = models.BooleanField(default=False)
#     parking = models.BooleanField(default=False)
#     sun_room = models.BooleanField(default=False)
#     concrete_flooring = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.property.title}"


class Rooms(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    bedrooms = models.CharField(choices=ROOM_CHOICES, max_length=30)
    washrooms = models.CharField(choices=ROOM_CHOICES, max_length=30)


    def __str__(self):
        return self.property.title



class OrderProperty(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.property.title}"

    def get_total_property_price(self):
        return self.quantity * self.property.price

    def get_total_discount_property_price(self):
        return self.quantity * self.property.discount_price

    def get_amount_saved(self):
        return self.get_total_property_price() - self.get_total_discount_property_price()

    def get_final_price(self):
        if self.property.discount_price:
            return self.get_total_discount_property_price()
        return self.get_total_property_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    property = models.ManyToManyField(OrderProperty)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_property in self.property.all():
            total += order_Property.get_final_price()
        total -= self.coupon.amount
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code



