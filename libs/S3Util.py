from botocore.exceptions import ClientError
import base64
import boto3
import hashlib
import logging

class S3Util:
    def __init__(self, bucket='missing-finder-bucket'):
        self.bucket = bucket
        self.s3_client = boto3.client('s3')

    def download_file(self, file_content, object_name=None):
        # Download file
        self.s3_client.download_fileobj(self.bucket, object_name, file_content)

    def move_file(self, source_file_path, target_file_path):
        copy_source = {
            'Bucket': self.bucket,
            'Key': source_file_path
        }
        
        self.s3_client.copy(CopySource=copy_source, Bucket=self.bucket, Key=target_file_path, ExtraArgs={'ACL': 'public-read'})
        self.s3_client.delete_object(Bucket=self.bucket, Key=source_file_path)

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
            self.s3_client.put_object(ACL='public-read', Body=file_content, Bucket=self.bucket, Key=object_name, ContentMD5=checksum, Metadata=metadata)
        except ClientError as e:
            logging.error(e)
