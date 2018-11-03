from flask import current_app
import boto3
import os


def uploadImage(localpath, S3path):
    status = True
    # Upload to S3 bucket
    S3_BUCKET = current_app.config['S3_BUCKET']
    S3_KEY = current_app.config['S3_KEY']
    S3_SECRET = current_app.config['S3_SECRET_ACCESS_KEY']
    S3_FILE_PATH = S3path

    # Create the instance connection to the S3 bucket
    s3 = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET
    )

    # Upload the file to the S3 bucket
    try:
        s3.upload_file(
            Bucket=S3_BUCKET,
            Filename=localpath,
            Key=S3_FILE_PATH
        )
    except Exception as e:
        current_app.logger.info('Upload QR code error: ' + str(e))
        status = False
    finally:
        # Remove the local QR code image
        os.remove(localpath)

    return status
