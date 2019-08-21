import os

def rename_sound_file(self, filename):
    upload_to = 'sound_files'
    ext = filename.split('.')[-1]
    filename = '{0}-{1}-id_{2}.{3}'.format(self.year, self.level, self.pk, ext)
    return os.path.join(upload_to, filename)