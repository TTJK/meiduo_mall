from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer as TJSSerializer
from django.conf import settings


def generate_save_user_token(openid):
    serializer = TJSSerializer(settings.SECRET_KEY,600)
    data = {'openid':openid}
    token = serializer.dumps(data)
    return token.decode()


def check_save_user_token(access_token):
    """
    将access_token还原为openid
    :param access_token: 签名后的openid
    :return: 原始的openid
    """
    # 创建序列化器对象，指定秘钥和过期时间（10分钟）
    serializer = TJSSerializer(settings.SECRET_KEY, 600)

    try:
        data = serializer.loads(access_token)
    except BadData:
        return None
    else:
        openid = data.get('openid')
        return openid