from django import http

def my_decorater(func):
    '''自定义装饰器，判断是否登录'''
    def wrapper(requset, *args, **kwargs):
        if requset.user.is_authenticated:
            # 如果用户登录，这进入这里，正常执行
            return func(requset, *args, **kwargs)
        else:
            # 如果用户未登录，则进入这里，返回400的状态码
            return http.JsonResponse({
                'code':400,
                'errmsg':'亲登录后重试'
            })
    return wrapper


class LoginRequiredMixin(object):
    '''自定义的Mixin扩展类'''

    # 重写的as_view方法
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        # 调用上面的装饰器进行过滤处理
        return my_decorater(view)