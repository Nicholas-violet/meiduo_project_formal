from django.shortcuts import render

# Create your views here.
from .models import User
from django.views import View
from django import http

class UsernameCountView(View):

    def get(self, request, username):

        count = User.objects.filter(username=username).count()

        return http.JsonResponse({
            'code':200,
            'errmsg':'ok',
            'count':count
        })


class MobileCountView(View):

    def get(self, request, mobile):

        count = User.objects.filter(mobile=mobile).count()

        return http.JsonResponse({
            'code':200,
            'errmsg':'ok',
            'count':count
        })





import json
import re
from django_redis import get_redis_connection
from django.contrib.auth import login,logout,authenticate

class RegisterView(View):

    def post(self, request):

        dict_msg = json.loads(request.body.decode())
        username = dict_msg.get('username')
        password = dict_msg.get('password')
        password2 = dict_msg.get('password2')
        mobile = dict_msg.get('mobile')
        allow = dict_msg.get('allow')
        sms_code = dict_msg.get('sms_code')

        # 判断是否缺少必传参数
        if not all([username,password,password2,mobile,allow]):
            return http.JsonResponse({
                'code':400,
                'errmsg':'缺少必须传递参数'
            })

        # 判断用户名是否正确
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({
                'code':400,
                'errmsg':'用户名格式有问题不正确'
            })

        # 判断密码格式是否正确
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({
                'code':400,
                'errmsg':'密码格式输入有误'
            })

        # 判断两次密码输入是否一致
        if password != password2:
            return http.JsonResponse({
                'code':400,
                'errmsg':'两次密码输入不一致'
            })

        # 电话号码格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({
                'code':400,
                'errmsg':'电话输入有误'
            })

        # 判断sms_code短信验证码格式是否正确
        if not re.match(r'^\d{6}$', sms_code):
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码不正确'
            })

        # 连接redis数据库，取出验证码
        conn = get_redis_connection('verify_code')
        sms_code_server = conn.get('sms_%s'%mobile)

        # 判断短信验证码是否存在，即是不是过期了
        if not sms_code_server:
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码已经过期'
            })

        # 判断数据库里面的和用户输入的验证码是否一致,从redis数据库里面取出来的是一个字节类型的
        if sms_code_server.decode() != sms_code:
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码有误！'
            })

        # 先判断allow的类型：


        # 判断allow是否允许
        if not allow:
            return http.JsonResponse({
                'code':400,
                'errmsg':'没有勾选用户协议'
            })

        # 保存到数据库
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except Exception as e:
            return http.JsonResponse({
                'code':400,
                'errmsg':'保存到数据库失败'
            })

        # 登录状态保持
        login(request, user)

        # 生成响应对象
        response = http.JsonResponse({
            'code':0,
            'errmsg':'ok'
        })

        # 在响应对象中深圳用户名信息，然后将有户名希尔cookie，设置时间为14
        response.set_cookie('username', user.username, max_age= 3600 * 24 * 14)

        # 返回响应结果
        return response


class LoginView(View):

    def post(self, request):

        dict_login = json.loads(request.body.decode())

        username = dict_login.get('username')
        password = dict_login.get('password')
        remembered = dict_login.get('remembered')

        # 必传参数是否完整
        if not all([username, password, remembered]):
            return http.JsonResponse({
                'code':400,
                'errmsg':'缺少必传参数'
            })

        # 验证是否可以登录
        user = authenticate(username=username,
                            password=password)

        # 判断是否可以登录user
        # if not user:
        if user is None:
            return http.JsonResponse({
                'code':400,
                'errmsg':'账户或者密码错误'
            })

        # 状态保持
        login(request, user)

        # 是否记住用户
        # if not remembered:
        if remembered != True:
            # 如果没有记住的话，就立刻失效
            request.session.set_expiry(0)
        else:
            # 如果设置 看，就睡设置两周为有效期，这是默认的
            request.session.set_expiry(None)

        # 生成相应对象
        response = http.JsonResponse({
            'code':0,
            'errmsg':'ok'
        })

        # 在响应对象里面设置用户信息，然后设置cookie，时间为14天
        response.set_cookie('username', user.username, max_age= 3600 * 24 * 14)

        # 返回响应结果
        return response





