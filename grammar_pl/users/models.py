from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.shortcuts import redirect

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from . import storage
from .helpers import rename_file_to_username


class CustomUser(AbstractUser):
    birth = models.DateField(null=True, blank=True, help_text='DD.MM.RR - na przykład 21.01.1999')
    avatar = models.ImageField(upload_to=rename_file_to_username, default="avatars/default.png",
                               storage=storage.OverwriteStorage())
    about = models.CharField(max_length=150, blank=True)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        #if user/superuser is created
        if self.id is None:
            #it allows me to avoid situation from below where it tries to get id of not existing user
            super(CustomUser, self).save()

        # gets the avatar of the userc
        this = CustomUser.objects.get(id=self.id)
        # checks if there is a change
        if this.avatar != self.avatar:
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
