import unittest
import json
from app import create_app, db
from app.models.base_models import Feature
from app.services import feature_service, customer_service, file_service


class TestService(unittest.TestCase):
    def setUp(self):
        # 初始化测试应用
        self.app = create_app("app.config.Test_config")
        self.app_context = self.app.app_context()
        self.app_context.push()

    def test_get_feature_by_category_tags_id(self):
        # 调用服务方法并验证结果
        result = file_service.generate_version_snapshot_service()
        print(result)

if __name__ == "__main__":
    unittest.main()