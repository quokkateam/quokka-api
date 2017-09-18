import boto3
import os
import base64

bucket_name = os.environ.get('S3_BUCKET')
region = os.environ.get('AWS_REGION_NAME')

s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ.get('S3_BUCKET'))

accepted_image_types = ['png', 'jpg', 'jpeg']


def upload_image(data=None, name=None, location='/'):
  type_info, body = data.split(',')

  image_type = False
  for ext in accepted_image_types:
    if 'image/{}'.format(ext) in type_info:
      image_type = ext
      break

  if not image_type:
    raise BaseException('Invalid image type: {}'.format(type_info))

  body = base64.b64decode(body)

  s3_file_path = '{}{}.{}'.format(location, name, image_type)

  bucket.put_object(
    Key=s3_file_path,
    Body=body,
    ContentType='image/{}'.format(image_type),
    ACL='public-read'
  )

  return 'https://s3-{}.amazonaws.com/{}/{}'.format(region, bucket_name, s3_file_path)