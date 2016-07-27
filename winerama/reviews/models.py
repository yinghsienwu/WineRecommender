from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

#In this first stage, our wine reviews app will contain two model entities: Wine and Review. A Wine has just a name. A Review has four fields: a name for the user that made the review, a wine rating, a publication date, and a text review. Additionally, each Review is associated with a Wine.

import numpy as np

class Wine(models.Model):
    name=models.CharField(max_length=200)
    def average_rating(self):
        all_ratings=map(lambda x: x.rating, self.review_set.all())
        return np.mean(all_ratings)
    
    def __unicode__(self):
        return self.name

class Review(models.Model):
    RATING_CHOICES=(
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
    )
    wine=models.ForeignKey(Wine) #tells Django each "Review" is related to a single "Wine"
    pub_date=models.DateTimeField('date published')
    user_name=models.CharField(max_length=100)
    comment=models.CharField(max_length=200)
    rating=models.IntegerField(choices=RATING_CHOICES)

class Cluster(models.Model):
    name=models.CharField(max_length=100)
    users=models.ManyToManyField(User)
    def get_members(self):
        return "\n".join([u.username for u in self.users.all()])



