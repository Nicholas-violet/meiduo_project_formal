from django.shortcuts import render

# Create your views here.
from django import http
from django.views import View
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha

class ImageCodeView(View):

    def get(self, request, uuid):
        """
        :param request:
        :param uuid:
        :return:
        """
        # 调用工具类，captcha生成图片以及对应文字
        text, image = captcha.generate_captcha()

        # 链接redis，获取链接对象
        redis_conn = get_redis_connection('verify_code')

        # 利用链接对象，保存到redis数据库，设置时间
        redis_conn.setex("img_%s"%uuid, 300, text)

        # 返回
        return http.HttpResponse(image, content_type='image/jpg')