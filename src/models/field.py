from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field as PydanticField, ConfigDict, model_validator
from src.models.condition import Condition, ConditionField
from src.models.type import FieldTypes


class Field(BaseModel):
    """表示字段（Field）的类"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    key: str
    description: str
    field_type: Optional[str] = None
    multi_type: List[str]
    item_type: Optional[str] = None
    item_multi_type: List[str]
    regex: Optional[str] = None
    regex_enabled: bool = False
    required: bool = False
    condition: Optional[Condition] = None
    children: List[Field] = PydanticField(default_factory=list)

    @model_validator(mode="before")
    def validate_condition(cls, data: dict):
        """在建立模型前檢查 condition 類型"""
        condition = data.get("condition")
        if condition is not None and not isinstance(condition, Condition):
            data["condition"] = None
        return data

    def __repr__(self):
        return (
            f"Field(key={self.key}, description={self.description}, "
            f"type={self.field_type}, item_type={self.item_type}, regex={self.regex}, "
            f"required={self.required}, condition={self.condition}, "
            f"children_count={len(self.children)})"
        )

    # ===== 常用方法 =====
    def is_required(self) -> bool:
        """返回字段是否必填"""
        return self.required

    def get_condition(self) -> Optional[Condition]:
        """返回字段的條件"""
        return self.condition

    def add_child(self, child_field: Field):
        """添加子字段"""
        self.children.append(child_field)

    def get_children(self) -> List[Field]:
        """获取子字段"""
        return self.children

    def update(
        self,
        description: Optional[str] = None,
        field_type: Optional[str] = None,
        item_type: Optional[str] = None,
        regex: Optional[str] = None,
        required: Optional[bool] = None,
    ) -> Field:
        """更新字段內容"""
        if description is not None:
            self.description = description
        if field_type is not None:
            self.field_type = field_type
        if item_type is not None:
            self.item_type = item_type
        if regex is not None:
            self.regex = regex
        if required is not None:
            self.required = required

        # 若必填則清除條件
        if self.required:
            self.condition = None
        return self

    # ===== 工廠方法 =====
    @classmethod
    def from_dict(cls, data: dict) -> Field:
        """從字典建立 Field 實例"""
        condition_data = data.get("condition")
        condition = None
        if condition_data:
            condition = Condition(
                logical=condition_data.get("logical"),
                conditions=[
                    ConditionField(con["key"], con["operator"], con["value"])
                    for con in condition_data.get("conditions", [])
                ],
            )

        children = [
            cls.from_dict(child) for child in data.get("children", [])
        ]

        return cls(
            key=data["key"],
            description=data.get("description", ""),
            multi_type=data.get("multi_type", []),
            item_multi_type=data.get("item_multi_type", []),
            regex=data.get("regex"),
            regex_enabled=data.get("regex_enabled", False),
            required=data.get("required", False),
            condition=condition,
            children=children,
        )
