from app import db, cache
from app.services import admin_service
from app.models.base_models import Monitor_File
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
import os

def modify_monitor_list(monitor_files=None, add: bool = True, allow: bool = True):
    if monitor_files is None:
        monitor_files = []
    try:
        all_files = []  # 存储所有需要添加的文件记录
        
        for item in monitor_files:
            # 删除操作
            if not add:
                # 先递归删除所有子目录和文件
                if item.get("is_directory"):
                    # 查找当前目录对象
                    current_dir = Monitor_File.query.filter_by(
                        server_path=item.get("server_path"),
                        parent_id=item.get("parent_id")
                    ).first()
                    if current_dir:
                        # 递归删除所有子项
                        def delete_children(parent_id):
                            children = Monitor_File.query.filter_by(parent_id=parent_id).all()
                            for child in children:
                                if child.is_directory:
                                    delete_children(child.id)
                                db.session.delete(child)
                        # 删除所有子项
                        delete_children(current_dir.id)
                        # 删除当前目录
                        db.session.delete(current_dir)
                else:
                    # 如果是文件，直接删除
                    db.session.query(Monitor_File).filter_by(
                        server_path=item.get("server_path"),
                        parent_id=item.get("parent_id")
                    ).delete()
                continue
                
            # 如果是目录，递归获取所有子文件
            if item.get("is_directory"):
                status_code, msg, directory_data = admin_service.get_directory_contents(item.get("server_path"))
                if status_code == 200 and directory_data:
                    def process_directory_items(items, parent_path, parent_id):
                        for dir_item in items:
                            server_path = dir_item["path"]
                            name = dir_item["name"]
                            # 构建客户端路径
                            relative_path = os.path.relpath(server_path, item.get("server_path"))
                            client_path = os.path.join(item.get("client_path"), relative_path).replace("\\", "/")
                            
                            monitor_item = {
                                "name": name,
                                "server_path": server_path,
                                "client_path": client_path,
                                "is_directory": dir_item["is_directory"],
                                "is_virtual_directory": False,
                                "parent_id": parent_id,
                                "is_empty": True if dir_item["is_directory"] else False,
                                "allow": allow
                            }
                            all_files.append(monitor_item)
                            
                            # 如果是目录，继续递归
                            if dir_item["is_directory"]:
                                sub_status, sub_msg, sub_data = admin_service.get_directory_contents(server_path)
                                if sub_status == 200 and sub_data:
                                    process_directory_items(sub_data["directories"], client_path, len(all_files))
                    
                    # 先添加当前目录
                    all_files.append(item)
                    # 处理子文件
                    process_directory_items(directory_data["directories"], item.get("client_path"), len(all_files))
            else:
                # 如果是文件，直接添加
                all_files.append(item)
        
        # 批量添加所有文件记录
        for file_item in all_files:
            monitor_file = Monitor_File(**file_item)
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

        # 组合查询条件并执行
        if filters:
            query = query.filter(and_(*filters))

        result = query.all()

        return 200, "查询成功", {
            "directories": [obj.to_dict() for obj in result],
            "total": len(result),
            "current_path": None,
        }

    except SQLAlchemyError as e:
        return 500, f"数据库查询失败: {str(e)}", None


def get_monitor_directory_content_by_client_path(client_path = None):
    """获取指定客户端路径下的直接子文件和目录
    Args:
        client_path: 客户端路径
    Returns:
        (status_code, message, data)
    """
    try:
        if client_path and client_path != "\\":
            # 首先查找目标目录
            parent = Monitor_File.query.filter_by(client_path=client_path, is_directory=True).first()
            if not parent:
                return 404, "目标目录不存在", None
            parent_id = parent.id
        else:
            # 如果未指定路径，则默认为根目录
            parent_id = 0
            client_path = "\\"

        # 查询该目录下的直接子项
        children = Monitor_File.query.filter_by(parent_id=parent_id).all()
        
        # 构造返回数据
        data = {
            "directories": [obj.to_dict() for obj in children],
            "current_path": client_path,
            "current_path_id": parent_id,
            "total": len(children)
        }
        
        return 200, "获取成功", data

    except Exception as e:
        return 500, f"查询失败: {str(e)}", None

