from enum import Enum
from pydantic import BaseModel


class FileType(str, Enum):
    FILE = "file"
    FOLDER = "folder"


class PrecheckFile(BaseModel):
    name: str
    file_type: FileType

    def __init__(self, name: str, file_type: FileType):
        super().__init__(name=name, file_type=file_type)

    def __repr__(self):
        return f"<PrecheckFile name='{self.name}' type='{self.file_type.value}'>"
