from django.shortcuts import render

# Create your views here.
import logging
logger = logging.getLogger('django')
from django import http
import random
from django.views import View
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from libs.yuntongxun.ccp_sms import CCP


# 图片验证码
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



class SMSCodeView(View):
    """
    短信验证码
    """
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号吧
        :return: json数据
        """
        # 首先是判断，是否是重复的使用手机号了，，后面已经设置了一个手机号进入redis，时间为1分钟
        # 接下来就是判断了
        redis_conn = get_redis_connection('verify_code')
        # 进入数据库后，首先获取redis的数据,这一个是获取的是手机号，因为时候设置的就是手机号
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 如果存在就代表，一分钟之内再一次的发送了短信，就返回发送频繁
        if send_flag:
            return http.JsonResponse({
                'code':400,
                'errmsg':'发送短信过于频繁'
            })

        # 1、接收参数
        # 客户发来的验证码
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2、校验参数
        if not all([image_code_client,uuid]):
            return http.JsonResponse({
                'code':400,
                'errmsg':'缺少必传参数'
            })

        # 3、创建连接诶到redis的对象
        redis_conn = get_redis_connection('verify_code')

        # 4. 提取图形验证码
        image_code_server = redis_conn.get('img_%s'%uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return http.JsonResponse({
                'code':400,
                'errmsg':'图形验证码失效'
            })

        # 5. 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error('图形验证码：{}'.format(e))

        # 6. 对比图形验证码
        # bytes转为字符串
        image_code_server = image_code_server.decode()
        # 忽略大小写
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({
                'code':400,
                'errmsg':'输入图形验证码有误'
            })

        # 7. 生成短信验证码：生成6位数验证码
        sms_code = '%06d'%random.randint(0,999999)
        logger.info(sms_code)

        # 创建redis管道
        pl = redis_conn.pipeline()
        # 将redis请求添加到队列

        # 8. 保存短信验证码
        # 短信验证码有效期单位是300秒,保存格式是，。电话：短信验证码
        # redis_conn.setex('sms_%s'%mobile, 300, sms_code)
        pl.setex('sms_%s'%mobile, 300, sms_code)

        # 往redis里面写入一个数据，写入什么不重要。时间重要
        # 我们把手机号写入，然后设置时间数据为60，如果过期就获取不到
        # redis_conn.setex('send_flag_%s'%mobile, 60, 1)
        pl.setex('send_flag_%s'%mobile, 60, 1)

        # 执行请求，这一个很重要！
        pl.execute()
        # 9. 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 10. 响应结果
        return http.JsonResponse({
            'code':200,
            'errmsg':'短信发送成功ok'
        })
