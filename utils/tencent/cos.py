# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author   : Zheng Xingtao
# File     : cos.py
# Datetime : 2020/9/23 上午9:11


from django.conf import settings
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosServiceError
from setting.variable import TENCENT_COS_ID, TENCENT_COS_KEY


def create_bucket(region, bucket):
    """
    创建腾讯的数据存储桶
    :param region: 区域名
    :param bucket: 桶名称
    :return:
    """
    region = region  # 替换为用户的 Region
    config = CosConfig(Region=region, SecretId=TENCENT_COS_ID, SecretKey=TENCENT_COS_KEY)
    client = CosS3Client(config)

    # 创建桶
    client.create_bucket(
        Bucket=bucket,
        ACL="public-read"
    )

    # 添加桶的跨域规则
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def upload_image(region, bucket, image_obj, image_name):
    region = region  # 替换为用户的 Region
    config = CosConfig(Region=region, SecretId=TENCENT_COS_ID, SecretKey=TENCENT_COS_KEY)
    client = CosS3Client(config)

    """高级上传接口（推荐）"""
    # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
    # client.upload_file(
    #     Bucket=bucket,
    #     LocalFilePath='cos_test.ico',  # 本地文件的路径
    #     Key='test.ico',  # 上传到桶之后的文件名
    # )

    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=image_obj,
        Key=image_name
    )

    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, image_name)


def delete_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key
    )


def check_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    data = client.head_object(
        Bucket=bucket,
        Key=key
    )

    return data


def delete_file_list(bucket, region, key_list):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects
    )


def credential(bucket, region):
    """ 获取cos上传临时凭证 """

    from sts.sts import Sts

    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 5,
        # 固定密钥 id
        'secret_id': settings.TENCENT_COS_ID,
        # 固定密钥 key
        'secret_key': settings.TENCENT_COS_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],
    }

    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict


def delete_bucket(bucket, region):
    """ 删除桶 """
    # 删除桶中所有文件
    # 删除桶中所有碎片
    # 删除桶
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    try:
        # 找到文件 & 删除
        while True:
            part_objects = client.list_objects(bucket)

            # 已经删除完毕，获取不到值
            contents = part_objects.get('Contents')
            if not contents:
                break

            # 批量删除
            objects = {
                "Quiet": "true",
                "Object": [{'Key': item["Key"]} for item in contents]
            }
            client.delete_objects(bucket, objects)

            if part_objects['IsTruncated'] == "false":
                break

        # 找到碎片 & 删除
        while True:
            part_uploads = client.list_multipart_uploads(bucket)
            uploads = part_uploads.get('Upload')
            if not uploads:
                break
            for item in uploads:
                client.abort_multipart_upload(bucket, item['Key'], item['UploadId'])
            if part_uploads['IsTruncated'] == "false":
                break

        client.delete_bucket(bucket)
    except CosServiceError as e:
        pass
