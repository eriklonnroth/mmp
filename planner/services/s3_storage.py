from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'mmp/media' 
    file_overwrite = True  # Overwrite existing files with same name
    default_acl = 'public-read'
    bucket_name = 'erik'
    region_name = 'lon1'
    endpoint_url = 'https://lon1.digitaloceanspaces.com'