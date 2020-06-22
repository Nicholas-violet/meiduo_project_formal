# 导入celery包之内导入Celery类
from celery import Celery

# 利用导入的celery创建对象
celery_app = Celery('meiduo')


# 吧刚刚创建的config配置给celery，里面的参数为我们创建的config配置文件
celery_app.config_from_object('celery_tasks.config')

# 让celery_app自动胡群殴去目标地址下的任务，自动捕捉tasks
celery_app.autodiscover_tasks(['celery_tasks.sms'])


