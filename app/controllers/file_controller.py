from flask import Blueprint, jsonify, request, send_file
from app.services import file_service
file_bp = Blueprint('file', __name__)

"""
管理mod目录，文件列表，下载mod的控制器
"""


@file_bp.route('/version', methods=['GET'])
def get_version():
    """
    对比客户端提交的当前版本与最新版本，返回许可文件列表及下载许可token。
    逻辑：
      1. 根据客户端提交的版本号查询当前版本记录；
      2. 如果当前版本与最新版本一致，则返回空差异文件列表（也生成一个token，可供后续调用）；
      3. 分别查询当前版本和最新版本的文件列表（通过关联中间表union_version_file）；
      4. 以文件的md5为标识，对比两份列表，计算出差异文件，生成许可文件列表；
      5. 生成token，以client_uuid和client_version为键缓存toekn，再以token缓存许可文件列表；
      6. 返回最新版本号、token和许可文件列表。
    """
    client_version = request.args.get('ver')
    client_uuid = request.headers.get('Authorization')
    if not client_uuid:
        return "没有有效标识符", 400
    status_code, msg, data = file_service.get_last_version(
        client_uuid, client_version)
    if status_code != 200:
        return msg, status_code
    else:
        return jsonify(data), 200


@file_bp.route('/download', methods=['GET'])
def download_file():
    """
    根据传入的 token 和 file_md5 下载文件，同时检查许可文件列表下载次数
    逻辑：
      1. 从缓存中获取 token 对应的许可文件列表；
      2. 检查许可列表中是否包含该文件（以文件的 md5 为标识），以及下载次数是为0（默认为3，可配置）；
      3. 如果下载次数已达上限，则拒绝本次下载；
      4. 如果许可有效，则更新下载次数，查询数据库获取文件服务端路径，
         并通过 send_file 返回文件内容（作为附件下载）。
    """
    token = request.headers.get('Authorization')
    file_md5 = request.args.get('file')
    if token is None:
        return "没有token，无权下载", 400
    if file_md5 is None:
        return "没有文件标识", 400
    status_code, msg, data = file_service.download_file(token, file_md5)
    if status_code != 200:
        return msg, status_code
    else:
        return send_file(data)