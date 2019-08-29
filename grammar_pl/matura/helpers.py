import os


def rename_sound_file(self, filename):
    upload_to = 'sound_files'
    ext = filename.split('.')[-1]
    filename = '{0}-{1}-id_{2}.{3}'.format(self.get_year(), self.get_level(), self.pk, ext)
    return os.path.join(upload_to, filename)


def rename_exam_file(self, filename):
    upload_to = 'pdfs'
    ext = filename.split('.')[-1]
    filename = '{0}.{1}'.format(self.slug_url, ext)
    return os.path.join(upload_to, filename)


def rename_exam_anwser_file(self, filename):
    upload_to = 'pdfs'
    ext = filename.split('.')[-1]
    filename = '{0}_anwsers.{1}'.format(self.slug_url, ext)
    return os.path.join(upload_to, filename)


def rename_image_file(self, filename):
    upload_to = 'images'
    ext = filename.split('.')[-1]
    filename = '{0}-{1}-id_{2}.{3}'.format(self.get_year(), self.get_level(), self.pk, ext)
    return os.path.join(upload_to, filename)
