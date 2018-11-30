from django.db import models
from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
# Create your models here.
from django.contrib.auth.models import AbstractUser

# Create your models here.
from . import constants
from django.conf import settings


class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.NullBooleanField(default=False,verbose_name='邮箱验证状态')
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        serializer = TJWSSerializer(settings.SECRET_KEY,constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {'id': self.id,'username': self.username}
        token = serializer.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email_url(token):
        serializer = TJWSSerializer(settings.SECRET_KEY,constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            user_id = data.get('id')
            username = data.get('username')
            try:
                user = User.objects.get(id= user_id,username = username)
            except User.DoesNotExist:
                return None
            else:
                return user

