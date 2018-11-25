from .yuntongxun.sms import CCP
from . import constants

from celery_tasks.main import celery_app
# 装饰器器将send_sms_code装饰为异步任务,并设置别名 @celery_app.task(name='send_sms_code')
@celery_app.task(name = 'send_sms_code')
def send_sms_code(mobile, sms_code):

    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)