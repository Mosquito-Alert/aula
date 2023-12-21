from django.test import TestCase
import boto3
from config.settings.base import env
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from aula.settings_local import BASE_DIR

AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")
S3_KEY = 'test_file'
DEFAULT_FILE_STORAGE = "main.storages.MediaRootS3Boto3Storage"
AWS_S3_ENDPOINT_URL = env("DJANGO_AWS_S3_ENDPOINT_URL")


# Create your tests here.
class UploadS3TestCase(TestCase):
    def test_upload_single_file(self):
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, endpoint_url=AWS_S3_ENDPOINT_URL)
        self.assertTrue( s3 is not None, "s3 connection not established" )
        retval = s3.upload_file(str(BASE_DIR) + "/main/fixtures/splash.png", AWS_STORAGE_BUCKET_NAME, S3_KEY)
        print(retval)


