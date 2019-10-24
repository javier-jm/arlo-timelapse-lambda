import os
from base64 import b64decode
from datetime import datetime

import boto3
from Arlo import Arlo

s3 = boto3.resource('s3')

USERNAME = os.environ['ARLO_USERNAME']
PASSWORD = os.environ['ARLO_PASSWORD']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):

    # Instantiating the Arlo object automatically calls Login(), which returns an oAuth token that gets cached.
    # Subsequent successful calls to login will update the oAuth token.
    arlo = Arlo(USERNAME, PASSWORD)
    # At this point you're logged into Arlo.

    # Get the list of devices and filter on device type to only get the camera.
    # This will return an array which includes all of the camera's associated metadata.
    cameras = arlo.GetDevices('camera')

    # For each camera found take the latest snapshot and upload to S3
    for i in range(len(cameras)):
        camera = cameras[i]
        upload_latest_snapshot(arlo, camera)

    return {
        'statusCode': 200
    }

def upload_latest_snapshot(arlo, camera):
    snapshot_url = camera.get("presignedLastImageUrl")
    # Store the latest camera image under the same place every time for each device
    filename = 'latest_' + camera.get('deviceId') + '.jpg'

    arlo.DownloadSnapshot(snapshot_url, '/tmp/' + filename)
    data = open('/tmp/' + filename, 'rb')
    s3.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=data)

    arlo.Logout()
    print('## Script complete at {}'.format(str(datetime.now())))

if __name__ == '__main__':
    lambda_handler({"time": "2018-01-01"}, None)
