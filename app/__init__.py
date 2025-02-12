from flask import Flask
from flask_caching import Cache
from app.middlewares import *
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.util.log_utils import logger

db = SQLAlchemy()
cache = Cache()
migrate = Migrate()


def create_app(config_class='app.config.Config'):
    # 初始化配置文件
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化组件
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # 修改 Jinja2 的分隔符
    app.jinja_env.variable_start_string = "[|"
    app.jinja_env.variable_end_string = "|]"

    # 注册蓝图
    from app.controllers.index_controller import index_bp
    app.register_blueprint(index_bp)
    from app.controllers.file_controller import file_bp
    app.register_blueprint(file_bp, url_prefix='/api/file')
    from app.controllers.manage_controller import manage_bp
    app.register_blueprint(manage_bp, url_prefix='/api/him')

    # 注册中间件
    app_before_request(app)
    app_after_request(app)
    app_exception_handler(app)

    # 初始化数据库和配置
    with app.app_context():
        db.create_all()

        # 读取数据库中的服务配置
        from app.services.manage_service import set_server_config_from_db
        set_server_config_from_db()

    logger.info("服务器启动完成")
    return app
