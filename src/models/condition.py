from typing import List, Optional, Any
from pydantic import BaseModel

class ConditionField(BaseModel):
    key: str
    operator: str
    value: Any

    def __init__(self, key: str, operator: str, value: Any):
        # 可以在這裡加入自訂邏輯
        print(f"Initializing ConditionField: {key=} {operator=} {value=}")
        super().__init__(key=key, operator=operator, value=value)

class Condition(BaseModel):
    logical: Optional[str] = None
    conditions: List[ConditionField] = []
