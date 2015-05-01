# encoding: utf-8

'''
Updated on Apr 28, 2015

@author: Jacob Sungwoon Lee
'''

from django.db import models


class Venue(models.Model):
    key = models.CharField(db_index=True, max_length=200)
    image_post_fix = models.CharField(db_index=True, max_length=200)
    version = models.CharField(db_index=True, max_length=10)

    @property
    def image_url(self):
        image_post_fix = self.image_post_fix
        if self.version == '2014':
            image_url = "http://54.67.62.180/2014/" + image_post_fix
        else:
            image_url = "http://54.67.62.180/2014_additional/" + image_post_fix
        return image_url

    def __str__(self):
        return self.image_post_fix