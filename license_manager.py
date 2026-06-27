import os
import uuid
import hashlib
import json
from datetime import datetime, timedelta

class LicenseValidator:
    def __init__(self, registry_folder="registry"):
        self.registry_folder = registry_folder

    def get_hwid(self):
        # Tạo mã định danh duy nhất dựa trên phần cứng máy
        hwid = str(uuid.getnode()) + os.environ.get('COMPUTERNAME', '')
        return hashlib.sha256(hwid.encode()).hexdigest()

    def validate(self):
        hwid = self.get_hwid()
        license_path = os.path.join(self.registry_folder, f"{hwid}.json")

        # Kiểm tra sự tồn tại của file license trên máy
        if not os.path.exists(license_path):
            # Lần đầu chạy: Tạo file dùng thử 24h
            self._create_license_file(license_path, hwid, days=1)
            return True, "Dùng thử 24h đã kích hoạt."

        with open(license_path, 'r') as f:
            data = json.load(f)
            expiry = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
            
            if datetime.now() < expiry or data.get('type') == 'permanent':
                return True, "License hợp lệ."
            else:
                return False, "License đã hết hạn."

    def _create_license_file(self, path, hwid, days):
        expiry = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        data = {"hwid": hwid, "expiry_date": expiry, "type": "trial"}
        with open(path, 'w') as f:
            json.dump(data, f)
