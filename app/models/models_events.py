from datetime import datetime
from sqlalchemy import event
from .base_models import Base_model
from .config_models import Server_Config


def before_insert(mapper, connect, target):
    # 插入前设置创建和更新时间
    target.created_date = datetime.now
    target.updated_date = datetime.now


def before_update(mapper, connect, target):
    # 更新前设置更新时间
    target.updated_date = datetime.now


event.listen(Base_model, 'before_insert', before_insert)
event.listen(Base_model, 'before_update', before_update)
event.listen(Server_Config, 'before_insert', before_insert)
event.listen(Server_Config, 'before_update', before_update)
