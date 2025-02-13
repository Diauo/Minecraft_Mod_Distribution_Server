from flask import current_app
from app import db, cache
from app.models.base_models import Monitor_File, Version, File
from app.models.union_models import Union_Version_File
from app.util import service_util
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
    # 到达windows和linux的根目录执行阻断
    if path.endswith(":") or path == ("/"):
        return 403, "访问阻止", None
        
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

def generate_version_snapshot_service():
    """
    版本快照生成服务
    1. 从 base_monitor_file 表中读取监控配置，
       根据 is_directory 判断目标是文件还是目录。
    2. 如果是文件，直接记录（前提是该文件未被排除）。
    3. 如果是目录，则递归扫描目录下所有文件，同时跳过被排除的文件或目录。
    4. 生成新的版本号，并将扫描得到的文件列表作为版本快照返回。

    版本更新可通过看门狗、定时任务或主动接口触发，本 service 仅实现版本快照生成逻辑。
    """
    try:
        # 查询允许监控的记录（允许监控的配置）
        allowed_records = db.session.query(Monitor_File).filter(
            Monitor_File.allow == True).all()
        # 查询排除的记录（需要排除的目录或文件）
        excluded_records = db.session.query(Monitor_File).filter(
            Monitor_File.allow == False).all()

        version_file_list = []

        for record in allowed_records:
            if record.is_directory:
                # 如果记录是目录，递归扫描该目录下的所有文件
                scanned_files = service_util.scan_directory(
                    record.server_path, record.client_path, allowed_records, excluded_records)
                version_file_list.extend(scanned_files)
            else:
                # 如果记录是文件，先确认该文件存在且不被排除
                if os.path.exists(record.server_path) and not service_util.is_excluded(record.server_path, allowed_records, excluded_records):
                    md5_val = service_util.compute_md5(record.server_path)
                    version_file_list.append({
                        "name": record.name,
                        "server_path": record.server_path,
                        "client_path": record.client_path,
                        "md5": md5_val
                    })

        # 生成新的版本号
        new_version = service_util.generate_new_version_number()

        # 插入版本信息
        new_version = Version(version=new_version)
        db.session.add(new_version)
        db.session.flush()  # 先提交版本表的记录，获取 version_id

        # 处理每个文件
        for file_info in version_file_list:
            server_path = file_info.get('server_path')
            md5_val = file_info.get('md5')
            client_path = file_info.get('client_path')

            # 检查文件是否已存在
            file_record = db.session.query(File).filter(
                File.md5 == md5_val, File.server_path == server_path).first()

            if file_record:
                # 如果文件已经存在，检查 client_path 是否发生变动
                if file_record.client_path != client_path:
                    # 如果变动了，更新 client_path
                    file_record.client_path = client_path
                    db.session.commit()
            else:
                # 如果文件不存在，插入新的文件记录
                file_record = File(
                    name=file_info['name'],
                    server_path=server_path,
                    client_path=client_path,
                    md5=md5_val
                )
                db.session.add(file_record)
                db.session.commit()

            # 关联文件和版本
            version_file_association = Union_Version_File(
                version_id=new_version.id, file_id=file_record.id)
            db.session.add(version_file_association)

        # 提交所有修改
        db.session.commit()
        return 200, "版本快照生成成功", {
            "version": new_version,
            "files": version_file_list
        }
    except Exception as e:
        db.session.rollback()
        return 500, f"版本快照生成异常: {str(e)}", None
