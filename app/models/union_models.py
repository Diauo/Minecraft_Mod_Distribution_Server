from app import db
from .base_models import Base_model


class Union_Version_File(Base_model):
    __tablename__ = 'union_version_file'

    version_id = db.Column(db.Integer, unique=False, nullable=False)
    file_id = db.Column(db.Integer, unique=False, nullable=False)
