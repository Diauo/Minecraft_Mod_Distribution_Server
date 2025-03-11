from flask import Blueprint, jsonify, request
from app.services import admin_service, file_service, monitor_service
admin_bp = Blueprint('admin', __name__)

"""
管理控制器
"""
@admin_bp.route('/monitor/modify', methods=['POST'])
def modify_monitor_list():
    """
    将一个目录/文件加入监控/排除列表或者从中移除
    应包含服务器文件路径与客户端映射路径
    修改文件列表5分钟（可配置）后，如果没有进一步动作，则触发一次文件列表版本更新动作
    """
    request_body = request.get_json()
    if request_body is None:
        return "没有有效的参数", 400
    if request_body.get("add") is None:
        return "没有指定操作方式[add]", 400
    if request_body.get("monitor_list") is None:
        return "没有监控列表[monitor_list]", 400
    add = request_body.get("add")
    allow = request_body.get("allow")
    monitor_files = request_body.get("monitor_list")
    status_code, msg, data = monitor_service.modify_monitor_list(monitor_files, add, allow)
    if status_code != 200:
        return msg, status_code
    else:
        return msg, 200


@admin_bp.route('/monitor/query', methods=['POST'])
def get_file_list():
    """
    查询监控列表
    """
    request_body = request.get_json()
    status_code, msg, data = monitor_service.query_monitor_files(request_body)
    if status_code != 200:
        return msg, 500
    else:
        return jsonify(data), 200

@admin_bp.route('/monitor/get_directory', methods=['POST'])
def get_monitor_directory():
    """
    获取监控目录
    """
    request_body = request.get_json()
    client_path = request_body.get("client_path")
    status_code, msg, data = monitor_service.get_monitor_directory_content_by_client_path(client_path)
    if status_code != 200:
        return msg, status_code
    else:
        return jsonify(data), 200

@admin_bp.route('/version/gen', methods=['GET'])
def gen_version():
    """
    生成版本列表
    """
    status_code, msg, data = admin_service.generate_version_snapshot_service()
    if status_code != 200:
        return msg, status_code
    else:
        return msg, 200


@admin_bp.route('/config/reload', methods=['GET'])
def reload_config():
    """
    重载配置文件
    """
    status_code, msg, data = admin_service.set_server_config_from_db()
    if status_code != 200:
        return msg, status_code
    else:
        return jsonify(data), 200


@admin_bp.route('/directory/get', methods=['POST'])
def get_directory_contents():
    """
    获取服务器上的目录与文件
    """
    request_body = request.get_json()
    path = request_body.get("path")
    filter = request_body.get("filter")
    status_code, msg, data = admin_service.get_directory_contents(path, filter)
    if status_code != 200:
        return msg, status_code
    else:
        return jsonify(data), 200


@admin_bp.route('/access_list/modify', methods=['POST'])
def modify_access_list():
    """
    将一个IP/UUID加入访问控制列表
    """
    status_code, msg, data = ""  # todo
    if status_code != 200:
        return msg, status_code
    else:
        return jsonify(data), 200


@admin_bp.route('/access_list/get', methods=['GET'])
def get_access_list():
    """
    获取当前访问控制列表
    """
    status_code, msg, data = ""  # todo
    if status_code != 200:
        return msg, status_code
    else:
        return jsonify(data), 200
