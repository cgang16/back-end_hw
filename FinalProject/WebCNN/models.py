import os
from django.db import models
from datetime import datetime
from FinalProject import settings
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


class User(models.Model):
    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=252, default="")
    createtime = models.DateTimeField(default=datetime.now)
    path = models.ImageField(upload_to='origin/',blank=True)


# 删除field同时删除media中图片
@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    try:
        path = instance.path.path
        if os.path.isfile(path):
            os.remove(path)
        rname = instance.filename + str(instance.id) + '.jpg'
        fname2 = os.path.join(settings.MEDIA_ROOT, 'results', rname)
        if os.path.isfile(fname2):
            os.remove(fname2)
    except:
        return
