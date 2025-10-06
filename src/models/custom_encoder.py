import json
from typing import LiteralString

from src.models.field import Field
from src.models.condition import Condition, ConditionField
from src.models.fileType import PrecheckFile


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        field = None

        if isinstance(obj, Field):
            field = {
                "key": obj.key,
                "description": obj.description,
                "multi_type": obj.multi_type,
                "item_multi_type": obj.item_multi_type,
                "regex": obj.regex,
                "regex_enabled": obj.regex_enabled,
                "required": obj.required,
                "condition": obj.condition,
                "children": obj.children
            }
        elif isinstance(obj, PrecheckFile):
            field = {
                "name": obj.name,
                "file_type": obj.file_type.value
            }

        elif isinstance(obj, Condition):
            field = {
                "logical": obj.logical,
                "conditions": obj.conditions
            }

        elif isinstance(obj, ConditionField):
            field = {
                "key": obj.key,
                "operator": obj.operator,
                "value": obj.value
            }

        return field



class ObjectToJsonFile:
    @staticmethod
    def to_json(file_name: str | LiteralString, obj: object) -> None:
        with open(file_name, "w") as file:
            json.dump(obj, file, cls=CustomEncoder, indent=4)
