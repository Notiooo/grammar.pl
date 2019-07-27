import os

def rename_file_to_username(self, filename):
    upload_to = 'avatars'
    ext = filename.split('.')[-1]
    filename = 'avatar_{}.{}'.format(self.username, ext)
    return os.path.join(upload_to, filename)