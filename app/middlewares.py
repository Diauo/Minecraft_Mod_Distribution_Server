from flask import request, jsonify, current_app
from fnmatch import fnmatch


def app_before_request(app):
    # 访问控制
    @app.before_request
    def access_check():
        # access_list = current_app.config.get('ACCESS_LIST', {})
        # access_list['UUID'] = access_list.get('UUID', 0) + 1
        # current_app.config['ACCESS_LIST'] = access_list
        # token = request.headers.get('Authorization')
        # UUID = request.headers.get('UUID')
        pass

    # 管理员访问鉴权
    @app.before_request
    def admin_access_check():
        authorization = request.headers.get('Authorization')

        pass


def app_after_request(app):
    # 格式化所有返回值
    @app.after_request
    def global_result_format(response):
        # 排除接口
        exclusion_list = current_app.config.get(
            'GLOBAL_RESULT_FORMAT_EXCLUSION_INTERFACE', [])
        normalized_path = request.path.rstrip('/')
        if any(fnmatch(normalized_path, pattern) for pattern in exclusion_list):
            return response
        # 只处理API的返回值
        if request.path.startswith("/api"):
            # 获取响应的原始数据
            response_data = response.get_json()
            response.headers["Content-Type"] = "application/json; charset=UTF-8"
            status = response.status_code == 200
            wrapped_response = {
                "status": status,
                "code": response.status_code,
                "data": response_data if response_data else response.get_data().decode()
            }
            # 请求成功，只是业务出错。覆写状态码，避免前端直接抛出异常
            response.status_code = 200
            response.set_data(jsonify(wrapped_response).data)
        return response

# 异常处理


def app_exception_handler(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        error_message = f"{type(e).__name__}: {str(e)}"
        return error_message, 500
