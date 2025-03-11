from app import db, cache
from flask import current_app
from sqlalchemy import text
import os
import uuid


def get_last_version(client_uuid, client_version=None):
    # 查询最新版本记录（按id降序，取最新一条）
    # todo 如果使用一个全局参数SERVER_VERSION即可实现回滚
    sql_latest = text(
        "SELECT id, version FROM base_version ORDER BY id DESC LIMIT 1")
    latest_result = db.session.execute(sql_latest)
    latest_row = latest_result.fetchone()
    if latest_row is None:
        return 404, "目前没有有效的mod列表", None

    latest_version_id = latest_row.id
    latest_version_str = latest_row.version

    # 如果当前版本已是最新版本
    if latest_version_str == client_version:
        return 200, "当前版本已是最新版本", {
            "version": latest_version_str,
            "license_files": []
        }

    # 检查缓存，如果之前获取过token则将token返回，并返回许可列表
    token = cache.get(f"client_version:{client_uuid}:{client_version}")
    license_files = cache.get(f"license_files:{token}")
    if license_files:
        return 200, "获取成功", {
            "version": latest_version_str,
            "token": token,
            "license_files": license_files
        }

    # 查询客户端提交的当前版本记录
    sql_current = text(
        "SELECT id, version FROM base_version WHERE version = :client_version LIMIT 1")
    current_result = db.session.execute(
        sql_current, {'client_version': client_version})
    current_row = current_result.fetchone()
    current_version_id = None
    if current_row is not None:
        current_version_id = current_row.id

    # 查询当前版本的文件列表，仅获取文件的md5值
    sql_client_files = text(
        "SELECT bf.md5 FROM base_file bf "
        "JOIN union_version_file uvf ON bf.id = uvf.file_id "
        "WHERE uvf.version_id = :version_id"
    )
    client_files_result = db.session.execute(
        sql_client_files, {'version_id': current_version_id})
    client_files = client_files_result.fetchall()
    # 用集合保存当前版本所有文件的md5，方便比对
    client_md5_set = {row.md5 for row in client_files}

    # 查询最新版本的文件列表，获取文件的md5、server_path和client_path等信息
    sql_latest_files = text(
        "SELECT bf.name, bf.md5, bf.server_path, bf.client_path FROM base_file bf "
        "JOIN union_version_file uvf ON bf.id = uvf.file_id "
        "WHERE uvf.version_id = :version_id"
    )
    latest_files_result = db.session.execute(
        sql_latest_files, {'version_id': latest_version_id})
    latest_files = latest_files_result.fetchall()

    # 获取最大下载次数（可配置，默认3次）
    max_download = current_app.config.get("FILE_MAX_DOWNLOAD_COUNT", 3)

    # 对比两份列表生成下载许可列表：对于最新版本中不存在于当前版本（以md5判断）的文件即为新增/修改的文件
    license_files = []
    for row in latest_files:
        if row.md5 not in client_md5_set:
            license_files.append({
                "name": row.name,
                "md5": row.md5,
                "downloadable_times": max_download,
                "client_path": row.client_path
            })

    # 生成下载许可token，并构造许可文件列表，每个文件下载次数初始为 0
    token = str(uuid.uuid4())

    # 将token与许可文件列表存入缓存
    cache.set(
        f"client_version:{client_uuid}:{client_version}", token, timeout=600)
    cache.set(f"license_files:{token}", license_files)
    # 返回结果：最新版本号、token、许可文件列表
    return 200, "获取成功", {
        "version": latest_version_str,
        "token": token,
        "license_files": license_files
    }


def download_file(token, file_md5):
    # 从内存中获取许可文件列表
    license_files = cache.get(f"license_files:{token}")
    if not license_files:
        return 401, "无效的下载许可token", None

    # 在许可列表中查找对应的文件 md5
    allowed = False
    for i, item in enumerate(license_files):
        if file_md5 == item.get('md5'):
            allowed = True
            current_count = item.get("downloadable_times", 0)
            if current_count <= 0:
                # 超过下载上限，则拒绝访问
                return 403, "该文件下载次数已达上限，拒绝访问", None
            # 更新下载次数：递减1次
            item['downloadable_times'] -= 1
            break

    if not allowed:
        return 403, "没有该文件的下载许可", None

    cache.set(f"license_files:{token}", license_files)

    # 查询数据库，使用 text 构造 SQL 查询文件的服务端路径
    sql_file = text(
        "SELECT server_path FROM base_file WHERE md5 = :file_md5 LIMIT 1")
    result = db.session.execute(sql_file, {'file_md5': file_md5})
    row = result.fetchone()
    if row is None:
        return 404, "文件记录不存在", None

    server_path = row.server_path
    # 检查实际文件是否存在
    if not os.path.exists(server_path):
        return 404, "文件未找到", None

    # 返回文件路径交由controller发送
    return 200, "成功", server_path

