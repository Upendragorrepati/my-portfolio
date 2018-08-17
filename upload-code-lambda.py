import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource("sns")
    topic = sns.Topic("arn:aws:sns:us-east-1:445891360755:deployPortfolioTopic")
    location={
        "bucketName": 'portfoliobuilt.upendra',
        "objectKey":   'portfoliobuilt.zip'

    }
    try:
        job=event.get('CodePipeline.job')
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location=artifact["location"]["s3Location"]

        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('port.upendra.info')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Message="Portfolio Deployed - Deploy Successfully",Subject="Portfolio Deployed")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job['id'])

    except Exception, e:
        topic.publish(Message="Portfolio Deployment Failed",Subject="Portfolio Deployment Failed")
        raise e

    return 'Hello From Lambda'
