from django.contrib.auth.backends import ModelBackend
import re
from .models import User


def get_user_by_account(account):
    '''判断account 是否为手机号码，返回user对象'''
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # account是手机号，然后根据手机号码去数据库里面查找，获取user对象返回
            user = User.objects.get(mobile=account)

        else:
            # account是用户名，然后根据用户名去数据库里面查找，获取user对象
            user = User.objects.get(username=account)
    except Exception as e:
        # 如果account不是用户名也不是手机号，就返回None
        return None
    else:
        # 如果得到user就返回user
        return user



# 继承自ModelBackend，重写authenticate函数
class UsernameMobileAuthBackend(ModelBackend):
    '''自定义用户认证后端'''

    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        重写认证方法，实现用户名和mobile登录功能
        :param request: 请求对象
        :param username: 用户名
        :param password: 密码
        :param kwargs: 其他参数
        :return: user
        '''

        # 自定义验证用户是否存在的函数
        # 更加传入的username获取user对象，username可以是手机号或者用户名
        user = get_user_by_account(username)

        # 校验user，是否存在并且校验密码是否正确
        if user and user.check_password(password):
            # 如果user存在，密码正确，这返回user
            return user