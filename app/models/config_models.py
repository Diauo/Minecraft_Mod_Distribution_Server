from app import db
from datetime import datetime


class Server_Config(db.Model):
    __tablename__ = "server_config"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(128), unique=False, nullable=False)
    value = db.Column(db.String(128), unique=False, nullable=False)
    type = db.Column(db.String(32), nullable=False, server_default='str')
    created_date = db.Column(db.DateTime, default=datetime.now)
    updated_date = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now)

    def get_converted_value(self):
        """根据 type 字段将 value 转换为相应的 Python 类型"""
        if 'int' == self.type:
            return int(self.value)
        elif 'float' == self.type:
            return float(self.value)
        elif 'bool' == self.type:
            return self.value.lower() in ('true', '1', 'yes')
        else:
            return self.value
