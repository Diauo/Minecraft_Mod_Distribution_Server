from flask import current_app
from app import db, cache
from app.models.base_models import Monitor_File
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from app.models.config_models import Server_Config
from app.util.log_utils import logger
from app.util import service_util
import os
import re


def verify_pin_code(ping):
    pass


def modify_monitor_list(monitor_files=None, add: bool = True):
    if monitor_files is None:
        monitor_files = []
    try:
        for item in monitor_files:
            # 先删除旧数据（使用 ORM 方式）
            db.session.query(Monitor_File).filter_by(
                server_path=item.get("server_path")).delete()
            # 如果是删除操作，跳过新增逻辑
            if not add:
                continue
            # 添加新数据
            monitor_file = Monitor_File(**item)
            db.session.add(monitor_file)
        db.session.commit()  # 统一提交事务
        return 200, "成功", None
    except Exception as e:
        db.session.rollback()  # 发生异常时回滚
        return 500, f"操作失败: {str(e)}", None


def query_monitor_files(request_body):
    try:
        query = db.session.query(Monitor_File)
        filters = []

        if request_body is not None:
            # 解析查询条件（动态构建 WHERE 语句）
            if "name" in request_body and request_body["name"]:
                filters.append(Monitor_File.name.like(
                    f"%{request_body['name']}%"))  # 模糊查询

            if "server_path" in request_body and request_body["server_path"]:
                filters.append(Monitor_File.server_path.like(
                    f"%{request_body['server_path']}%"))

            if "client_path" in request_body and request_body["client_path"]:
                filters.append(Monitor_File.client_path.like(
                    f"%{request_body['client_path']}%"))

            if "is_directory" in request_body and request_body["is_directory"] is not None:
                filters.append(Monitor_File.is_directory ==
                               request_body["is_directory"])  # 精确匹配

            if "allow" in request_body and request_body["allow"] is not None:
                filters.append(Monitor_File.allow ==
                               request_body["allow"])  # 精确匹配

            if "created_date_start" in request_body and request_body["created_date_start"]:
                filters.append(Monitor_File.created_date >=
                               request_body["created_date_start"])  # 开始时间

            if "created_date_end" in request_body and request_body["created_date_end"]:
                filters.append(Monitor_File.created_date <=
                               request_body["created_date_end"])  # 结束时间

            if "updated_date_start" in request_body and request_body["updated_date_start"]:
                filters.append(Monitor_File.updated_date >=
                               request_body["updated_date_start"])  # 开始时间

            if "updated_date_end" in request_body and request_body["updated_date_end"]:
                filters.append(Monitor_File.updated_date <=
                               request_body["updated_date_end"])  # 结束时间
        else:
            request_body = {}
        # 处理分页参数（默认第一页，每页10条）
        page = int(request_body.get("page", 1))
        size = int(request_body.get("size", 10))

        # 组合查询条件并执行
        if filters:
            query = query.filter(and_(*filters))

        # 执行分页查询
        paginated_result = query.paginate(
            page=page, per_page=size, error_out=False)

        return 200, "查询成功", {
            "result": [obj.to_dict() for obj in paginated_result.items],
            "total": paginated_result.total,
            "pages": paginated_result.pages,
            "current_page": paginated_result.page
        }

    except SQLAlchemyError as e:
        return 500, f"数据库查询失败: {str(e)}", None


def set_server_config_from_db():
    configs = Server_Config.query.all()
    for config in configs:
        current_app.config[config.key] = config.get_converted_value()
    logger.info("服务器配置载入完成")
    return 200, "服务器配置载入完成", None

@cache.memoize(timeout=60)
def get_directory_contents(path=None, filter_pattern=None):
    """
    获取指定路径下的目录和文件列表，并根据文件名正则进行过滤
    :param path: 当前访问的路径
    :param filter_pattern: 可选的正则过滤模式，默认不进行过滤
    :return: 包含文件和目录列表以及当前路径的JSON响应
    """
    # 如果没有传递路径，使用默认路径
    if not path:
        path = service_util.get_default_path()

    # 检查路径是否存在
    if not os.path.exists(path):
        return 404, "路径不存在", None

    # 处理文件和目录列表
    directories = []
    files = []

    try:
        # 遍历指定路径下的文件和目录
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)

            # 过滤文件名，支持正则
            if filter_pattern:
                if not re.search(filter_pattern, entry):
                    continue  # 如果文件名不匹配正则，则跳过

            # if os.path.isdir(entry_path):
            #     directories.append(entry)
            # else:
            #     files.append(entry)

            # 获取文件的详细信息（大小、最后修改时间）
            if os.path.isdir(entry_path):
                directories.append({
                    "name": entry,
                    "path": entry_path
                })
            else:
                file_size, file_mtime = service_util.get_file_details(
                    entry_path)
                files.append({
                    "name": entry,
                    "path": entry_path,
                    "size": file_size,  # 文件大小（字节）
                    "last_modified": file_mtime
                })

        # 返回当前路径下的目录和文件列表，以及当前路径信息
        return 200, "读取成功", {
            "directories": directories,
            "files": files,
            "current_path": path,
            "count": len(directories) + len (files)
        }
    except Exception as e:
        return 500, f"读取路径出错: {str(e)}", None
