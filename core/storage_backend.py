from storages.backends.s3 import S3Storage

class mediaStoarge(S3Storage):
    location = "profile"
    file_overwrite = True
    default_acl = None

