from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from . import storage

import os


def rename_file_to_username(instance, filename):
    upload_to = 'avatars'
    ext = filename.split('.')[-1]
    filename = 'avatar_{}.{}'.format(instance.username, ext)
    return os.path.join(upload_to, filename)


class CustomUser(AbstractUser):
    birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to=rename_file_to_username, default="avatars/default.png",
                               storage=storage.OverwriteStorage())
    about = models.CharField(max_length=150, blank=True)


    def get_absolute_url(self):
        return reverse('profile', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        if self.avatar:
            # Opening the uploaded image
            im = Image.open(self.avatar).convert('RGB')
            output = BytesIO()
            # Resize/modify the image
            im = im.resize((400, 400))
            # after modifications, save it to the output
            im.save(output, format='JPEG', quality=80)
            output.seek(0)
            # change the imagefield value to be the newley modifed image value
            self.avatar = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.avatar.name.split('.')[0],
                                               'image/jpeg',
                                               sys.getsizeof(output), None)
            super(CustomUser, self).save()
