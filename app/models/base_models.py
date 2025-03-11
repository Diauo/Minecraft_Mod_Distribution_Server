from app import db
from datetime import datetime
from sqlalchemy.types import TypeDecorator, DateTime

class FormattedDateTime(TypeDecorator):
    impl = DateTime

    def process_bind_param(self, value, dialect):
        return value  # 插入时保持 datetime 类型

    def process_result_value(self, value, dialect):
        return value.strftime('%Y-%m-%d %H:%M:%S') if value else None  # 查询时格式化
    
class Base_model(db.Model):
    __tablename__ = "base"
    __abstract__ = True  # 标记为抽象类，不会映射到具体的表

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(FormattedDateTime, default=datetime.now)
    updated_date = db.Column(FormattedDateTime, default=datetime.now, onupdate=datetime.now)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        name = getattr(self, 'name', '无名model')
        return f"<{name}>"

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            data[column.name] = getattr(self, column.name)
        return data


class Version(Base_model):
    __tablename__ = 'base_version'
    __info__ = '''文件列表版本
    '''
    version = db.Column(db.String(64), unique=True, nullable=False)
    files = []


class File(Base_model):
    __tablename__ = 'base_file'
    __info__ = ''' 文件
    '''
    name = db.Column(db.String(64), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=True)
    type = db.Column(db.String(64), unique=False, nullable=True)  # 文件类型
    server_path = db.Column(db.String(256), unique=False, nullable=False)
    client_path = db.Column(db.String(256), unique=False, nullable=False)
    md5 = db.Column(db.String(64), unique=False, nullable=False)


class Monitor_File(Base_model):
    __tablename__ = 'base_monitor_file'
    __info__ = ''' 监控文件或者目录
    '''
    name = db.Column(db.String(64), unique=False, nullable=False)
    server_path = db.Column(db.String(256), unique=False, nullable=False)
    client_path = db.Column(db.String(256), unique=False, nullable=False)
    is_directory = db.Column(db.Boolean, unique=False, nullable=False)  # 目录还是文件
    is_virtual_directory = db.Column(db.Boolean, unique=False, nullable=False)  # 是否是虚拟目录
    parent_id = db.Column(db.Integer, db.ForeignKey('base_monitor_file.id'), nullable=True)  # 上级目录ID
    is_empty = db.Column(db.Boolean, unique=False, nullable=False, default=True)  # 目录是否为空
    allow = db.Column(db.Boolean, unique=False, nullable=False)  # 允许下发或者排除


class Access_list(Base_model):
    __tablename__ = 'base_access_list'
    __info__ = ''' 访问列表
        '''
    UUID = db.Column(db.String(64), unique=False, nullable=True)
    ip_addr = db.Column(db.String(64), unique=False, nullable=True)
    allow = db.Column(db.Boolean, unique=False, nullable=False)