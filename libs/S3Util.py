from botocore.exceptions import ClientError
import base64
import boto3
import hashlib
import logging

class S3Util:
    def __init__(self, bucket='mantovanellos-bucket'):
        self.bucket = bucket
        self.s3_client = boto3.client('s3')

    def download_file(self, file_content, object_name=None):
        # Download file
        self.s3_client.download_fileobj(self.bucket, object_name, file_content)

    def upload_file(self, file_content, object_name=None):
        # Hash file content to calculate md5 checksum and send to AWS S3 verification
        hasher = hashlib.md5(file_content)
        digest = hasher.digest()
        checksum = base64.b64encode(digest).decode('utf-8')
    
        # Include md5 checksum as metadata
        metadata = {
            "md5_checksum": checksum
            }
        
        # Upload the file
        try:
            self.s3_client.put_object(Body=file_content, Bucket=self.bucket, Key=object_name, ContentMD5=checksum, Metadata=metadata)
        except ClientError as e:
            logging.error(e)
