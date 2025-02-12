from flask import current_app
import os
import hashlib
from datetime import datetime


def model_to_dict(result, clazz):
    data_list = [clazz(**row._asdict()) for row in result]
    data_list_dict = [data.__dict__ for data in data_list]
    for data in data_list_dict:
        data.pop('_sa_instance_state', None)
    return data_list_dict


def compute_md5(file_path):
    """计算文件的 MD5 值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        return None
    return hash_md5.hexdigest()


def get_default_path():
    """
    获取默认的路径。如果配置文件中没有定义，系统会根据操作系统自动选择。
    - Linux: 使用 home 目录
    - Windows: 使用桌面目录
    :return: 默认路径
    """
    # 尝试从配置文件读取路径
    default_path = current_app.config.get('DEFAULT_PATH')

    if default_path:
        return default_path  # 如果配置文件中定义了路径，直接返回

    # 如果没有配置，自动选择路径
    if os.name == 'nt':  # Windows
        # Windows的默认路径是用户桌面
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')
    elif os.name == 'posix':  # Linux
        # Linux的默认路径是用户的home目录
        return os.path.expanduser("~")
    else:
        # 如果是其他操作系统，默认返回空路径
        return "/"


def generate_new_version_number():
    """生成新的版本号，例如 'v20250210_1530' """
    now = datetime.datetime.now()
    return "v" + now.strftime("%Y%m%d_%H%M%S")


def is_excluded(path, allowed_records, excluded_records):
    """
    判断给定路径是否应被排除（排除规则的优先级较低，因为允许优先）
    :param path: 待检查的文件或目录路径
    :param allowed_records: 允许监控的 Monitor_File 记录（allow == True）
    :param excluded_records: 排除的 Monitor_File 记录（allow == False）
    :return: 如果 path 应被排除则返回 True，否则返回 False
    """
    norm_path = os.path.normpath(path)

    # 先检查允许规则，允许的优先级更高
    for rec in allowed_records:
        rec_path = os.path.normpath(rec.server_path)
        # 如果允许规则为目录，则判断路径是否以该目录为前缀（注意加上分隔符以防止误判）
        if rec.is_directory:
            if norm_path == rec_path or norm_path.startswith(rec_path + os.sep):
                # 明确在允许范围内，不排除
                return False
        else:
            # 如果允许规则为文件，则要求完全匹配
            if norm_path == rec_path:
                return False

    # 然后检查排除规则
    for rec in excluded_records:
        rec_path = os.path.normpath(rec.server_path)
        if rec.is_directory:
            if norm_path == rec_path or norm_path.startswith(rec_path + os.sep):
                return True
        else:
            if norm_path == rec_path:
                return True
    return False


def scan_directory(dir_path, base_client_path, allowed_records, excluded_records):
    """
    递归扫描目录，返回该目录下所有文件的信息
    :param dir_path: 被扫描的目录的 server_path
    :param base_client_path: 该目录对应的客户端路径前缀
    :param excluded_records: 排除规则列表（Monitor_File 对象，allow == False）
    :return: 文件列表，每个元素为字典，包含文件名、server_path、md5 值
    """
    file_list = []

    # 判断目录是否存在，如果不存在直接返回空列表
    if not os.path.exists(dir_path):
        return file_list

    # 遍历目录和子目录
    for root, dirs, files in os.walk(dir_path):
        # 对于当前目录中的文件进行排除检查
        for file in files:
            file_path = os.path.join(root, file)
            # 如果文件符合排除规则，则跳过
            if is_excluded(file_path, allowed_records, excluded_records):
                continue
            # 计算相对于扫描目录的相对路径，用于构造客户端路径
            relative_path = os.path.relpath(file_path, dir_path)
            client_file_path = os.path.join(base_client_path, relative_path)
            # 计算文件的 MD5
            md5_val = compute_md5(file_path)
            # 将符合条件的文件添加到文件列表
            file_list.append({
                "name": file,
                "server_path": file_path,
                "client_path": client_file_path,
                "md5": md5_val
            })

    return file_list

def get_file_details(file_path):
    """
    获取文件的详细信息：文件大小和最后修改时间
    :param file_path: 文件路径
    :return: 文件大小（bytes）、最后修改时间（格式化的字符串）
    """
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 获取文件的最后修改时间
    file_mtime = os.path.getmtime(file_path)
    file_mtime = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    return file_size, file_mtime