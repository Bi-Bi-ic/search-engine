from uuid import uuid4
import time, datetime
import base64, bcrypt, hashlib, os

URL_SERVER = os.getenv("URL_SERVER")
class ImageEntity():

    #constructor
    def __init__(self, texture):
        """
        Class constructor
        """
        self.texture = texture
        self.link = URL_SERVER

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def generate_id(self):
        self.id = uuid4()
        return

    def hash_name_generator(self, filename):
        sum_hash = filename + str(self.id)
        hash_name = bcrypt.hashpw(sum_hash.encode('utf-8'), bcrypt.gensalt())

        self.hash_name = hashlib.md5(hash_name).hexdigest()
        return

    def make_symlink(self):
        self.link += self.hash_name

