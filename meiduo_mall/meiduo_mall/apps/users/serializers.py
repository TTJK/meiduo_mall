import re
from rest_framework_jwt.settings import api_settings
from django_redis import get_redis_connection
from rest_framework import serializers
from .models import User, Address
from celery_tasks.email.tasks import send_verify_email

class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='token',read_only=True)
    class Meta:
        model = User
        fields = ['id','username','password','password2','mobile','sms_code','allow','token']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self,value):
        if not re.match(r"^1[3-9]\d{9}$",value):
            raise serializers.ValidationError('手机格式错误')
        return value

    def validate_allow(self,value):
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("两次输入密码不一致")


        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s'%mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        return data
    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()


        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载进行生成token的函数

        payload = jwt_payload_handler(user)  # 通过传用用户信息进行生成载荷
        token = jwt_encode_handler(payload)  # 根据载荷内部再拿到内部的header 再取到SECRET_KEY 进行HS256加密最后把加它们拼接为完整的token
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','mobile','email','email_active']

class EmailSerializer(serializers.ModelSerializer):
    """保存邮箱的序列化器"""
    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):

        """重写此方法有两个目的: 1.只保存邮箱, 2.发激活邮件"""
        instance.email = validated_data.get('email')
        instance.save()  # ORM中 的保存
        # super(EmailSerializer, self).update(instance, validated_data)
        # 1.1 生成邮箱的激活链接
        verify_url = instance.generate_verify_email_url()
        # 2.发激活邮件
        # 传入收件人及激活链接
        send_verify_email.delay(instance.email, verify_url)

        return instance

class AddressTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('title',)

class UserAddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user','is_deleted','create_time','update_time')



    def validata_mobile(self,value):
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self,validated_data):
        validated_data['user'] = self.context['request'].user
        print(validated_data)
        address = Address.objects.create(**validated_data)
        return address