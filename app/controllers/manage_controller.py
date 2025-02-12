from flask import Blueprint, jsonify, request
from app.services import manage_service, file_service
manage_bp = Blueprint('manage', __name__)

"""
管理控制器
"""


@manage_bp.route('/modify_monitor', methods=['POST'])
def modify_monitor_list():
    """
    将一个目录/文件加入监控/排除列表或者从中移除
    应包含服务器文件路径与客户端映射路径
    修改文件列表5分钟（可配置）后，如果没有进一步动作，则触发一次文件列表版本更新动作
    test路径：
    C:\\Users\\admin\\Desktop\\工程调度中心\\mctest\\mods
    """
    request_body = request.get_json()
    if request_body is None:
        return "没有有效的参数", 400
    if request_body.get("add") is None:
        return "没有指定操作方式[add]", 400
    if request_body.get("monitor_list") is None:
        return "没有监控列表[monitor_list]", 400
    add = request_body.get("add")
    monitor_files = request_body.get("monitor_list")
    status_code, msg, data = manage_service.modify_monitor_list(monitor_files, add)
    if status_code != 200:
        return msg, 500
    else:
        return msg, 200


@manage_bp.route('/query_monitor', methods=['POST'])
def get_file_list():
    """
    查询监控列表
    """
    request_body = request.get_json()
    status_code, msg, data = manage_service.query_monitor_files(request_body)
    if status_code != 200:
        return msg, 500
    else:
        return jsonify(data), 200


@manage_bp.route('/gen_version', methods=['GET'])
def gen_version():
    """
    生成版本列表
    """
    status_code, msg, data = file_service.generate_version_snapshot_service()
    if status_code != 200:
        return msg, 500
    else:
        return msg, 200


@manage_bp.route('/reload_config', methods=['GET'])
def reload_config():
    """
    重载配置文件
    """
    status_code, msg, data = manage_service.set_server_config_from_db()
    if status_code != 200:
        return msg, 500
    else:
        return jsonify(data), 200


@manage_bp.route('/get_directory', methods=['POST'])
def get_directory_contents():
    """
    获取服务器上的目录与文件
    """

    request_body = request.get_json()
    path = request_body.get("path")
    filter = request_body.get("filter")
    status_code, msg, data = manage_service.get_directory_contents(path, filter)
    if status_code != 200:
        return msg, 500
    else:
        return jsonify(data), 200


@manage_bp.route('/modify_access_list', methods=['POST'])
def modify_access_list():
    """
    将一个IP/UUID加入访问控制列表
    """
    status_code, msg, data = ""  # todo
    if status_code != 200:
        return msg, 500
    else:
        return jsonify(data), 200


@manage_bp.route('/get_access_list', methods=['GET'])
def get_access_list():
    """
    获取当前访问控制列表
    """
    status_code, msg, data = ""  # todo
    if status_code != 200:
        return msg, 500
    else:
        return jsonify(data), 200
