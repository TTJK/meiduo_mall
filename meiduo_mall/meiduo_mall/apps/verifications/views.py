import random

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from meiduo_mall.libs.yuntongxun.sms import CCP
from meiduo_mall.utils.exceptions import logger
from . import constants
from celery_tasks.sms.tasks import send_sms_code
class SMSCodeView(APIView):

    def get(self,request,mobile):
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({"message":"频繁发送短信"},status=status.HTTP_400_BAD_REQUEST)
        sms_code = "%06d" % random.randint(0,999999)
        logger.info(sms_code)
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex('sm_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()
        # redis_conn.setex('send_flag_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        # CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES //60],constants.SMS_CODE_TEMPLATE_ID)
        send_sms_code.delay(mobile, sms_code)
        return Response ({'message': 'OK'})
        