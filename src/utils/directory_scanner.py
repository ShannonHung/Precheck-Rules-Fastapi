import os
from typing import List

from src.models.fileType import PrecheckFile, FileType


class DirectoryScanner:
    def __init__(self, path="."):
        self.path = path

    def list_items(self) -> List[PrecheckFile]:
        items = []
        if not os.path.exists(self.path):
            return items
        for entry in os.listdir(self.path):
            full_path = os.path.join(self.path, entry)
            if os.path.isfile(full_path):
                file_type = FileType.FILE
            elif os.path.isdir(full_path):
                file_type = FileType.FOLDER
            else:
                continue
            items.append(PrecheckFile(entry, file_type))
        return items