import os
import os.path as op
import uuid

import aiofiles
from fastapi import File

from src.core.config import settings


class FileManager(object):
    def __init__(
        self,
        base_path=None,
        relative_path=None,
        name_generate=None,
        allow_extensions=None,
        permission=0o755,
        **kwargs
    ):
        if hasattr(settings, "UPLOAD_DIR"):
            base_dir = settings.UPLOAD_DIR
        if not base_dir:
            raise Exception("Config missing from UPLOAD_DIR")
        self.base_path = base_path
        self.relative_dir = relative_path
        self.name_generate = name_generate or uuid_name_gen
        if hasattr(settings, "FILE_ALLOWED_EXTENSIONS"):
            self.allow_extensions = settings.FILE_ALLOWED_EXTENSIONS
        else:
            self.allow_extensions = allow_extensions
        self.permission = permission
        self._should_delete = False

    def is_file_allowed(self, filename):
        if not self.allow_extensions:
            return True
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allow_extensions
        )

    def generate_name(self, obj, file_data):
        return self.name_generate(file_data)

    def get_path(self, filename):
        if not self.base_path:
            raise ValueError("FileUploadFiled field requires base path to be set")
        return op.join(self.base_path, filename)

    async def delete_file(self, filename):
        path = self.get_path(filename)
        if await aiofiles.path.exists(path):
            await aiofiles.remove(path)

    def save_file(self, data, filename):
        filename_ = filename.filename
        path = self.get_path(filename)
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission)
        data.save(path)
        return filename_


def uuid_name_gen(file_data: File):
    return str(uuid.uuid4()) + "_spe_" + file_data.filename
