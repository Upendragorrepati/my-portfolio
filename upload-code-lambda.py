import boto3
from botocore.client import Config
import zipfile
import mimetypes

s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

build_bucket = s3.Bucket('serverless-portfolio-mario-automated')
portfolio_bucket = s3.Bucket('serverless-portfolio-mario')

# On Windows, this will need to be a different location than /tmp
build_bucket.download_file('artifacts.zip', '/tmp/portfolio.zip')

with zipfile.ZipFile('/tmp/portfolio.zip') as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        portfolio_bucket.upload_fileobj(obj, nm,
          ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
        portfolio_bucket.Object(nm).Acl().put(ACL='public-read')