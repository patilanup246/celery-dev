"""Google Cloud Storage APIs helpers"""
import os
import boto
# import gcs_oauth2_boto_plugin
from boto.s3.keyfile import KeyFile
from google.cloud import storage
from os.path import join, dirname


class G3(object):
    DEFAULT_PROJECT_ID = 'xomad-1084'
    GOOGLE_STORAGE = 'gs'
    LOCAL_STORAGE = 'file'
    BRAND_AVATARS_BUCKET = 'x-static'

    _project_id = None
    _headers = {}

    def __init__(self, project_id=None):
        self.project_id = project_id or self.DEFAULT_PROJECT_ID

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    def project_id(self, value):
        self._project_id = value
        if value:
            self._headers = {'x-goog-project-id': value}

    def buckets(self, **kwargs):
        uri = self._google_storage_uri(**kwargs)
        return uri.get_all_buckets(headers=self._headers)

    def bucket(self, bucket_name, **kwargs):
        """Returns Bucket instance by a given name"""
        return self._google_storage_uri(bucket_name, **kwargs).get_bucket()

    def keys(self, bucket_name):
        return self.bucket(bucket_name).get_all_keys()

    def download(self, path, output_dir=None, **kwargs):
        try:
            src_uri = self._google_storage_uri(path, **kwargs)
            output_file = os.path.join(output_dir, path) if output_dir else path
            local_uri = self._local_storage_uri(output_file)
            local_uri.new_key().set_contents_from_file(KeyFile(src_uri.get_key()))
            return output_file
        except Exception as e:
            return None

    def download_key(self, key, output_dir=None):
        try:
            path = '%s/%s' % (key.bucket.name, key.name)
            output_file = os.path.join(output_dir, path) if output_dir else path
            local_uri = self._local_storage_uri(output_file)
            local_uri.new_key().set_contents_from_file(KeyFile(key))
            return output_file
        except Exception as e:
            return None

    @staticmethod
    def upload(blob_name, bucket_name, file_name=None, file_object=None):
        client = storage.Client.from_service_account_json(join(dirname(__file__), 'Xomad-2dbe29599526-duc.ho.json'))
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        # if blob.exists():
        #     print '%s already exists' % blob_name
        #     return blob.public_url
        if file_name:
            blob.upload_from_filename(file_name)
        else:
            blob.upload_from_string(file_object)
        return blob.public_url

    def _google_storage_uri(self, uri='', **kwargs):
        return boto.storage_uri(uri, self.GOOGLE_STORAGE, **kwargs)

    def _local_storage_uri(self, uri='', **kwargs):
        return boto.storage_uri(uri, self.LOCAL_STORAGE, **kwargs)


