# main.py
import json
import os
import shutil
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.models import CustomEncoder, Field
from src.models.api_response import APIResponse
from src.models.fileType import PrecheckFile, FileType
from src.utils import FieldLoader
from src.utils.directory_scanner import DirectoryScanner
from src.utils.json_loader import check_folder, save_json

app = FastAPI()

# 允許跨域
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_PATH = "./assets"  # 使用者不能離開這個根目錄


def file_load_check(target_path: str, is_file: bool = True) -> str:
    abs_target = os.path.abspath(target_path)
    abs_base = os.path.abspath(BASE_PATH)

    if not abs_target.startswith(abs_base):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.exists(abs_target):
        raise HTTPException(status_code=404, detail="File not found")
    if is_file and not abs_target.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Not a JSON file")

    return abs_target

def get_abs_path(path, is_file: bool = True):
    relative_path = path.strip("/")
    target_path = os.path.join(BASE_PATH, relative_path)
    return file_load_check(target_path, is_file)

@app.get("/api/files")
def list_files(
    path: str = Query("", description="Relative path"),
    show_type: str | None = Query(None, description="file / folder / all")
):
    abs_path = get_abs_path(path, False)
    scanner = DirectoryScanner(abs_path)
    all_items = scanner.list_items()

    if show_type in ("file", "folder"):
        filtered = [item for item in all_items if item.file_type.value == show_type]
    else:
        filtered = all_items

    filtered.sort(key=lambda item: (item.file_type != FileType.FOLDER, item.name.lower()))

    return JSONResponse(
        content=json.loads(json.dumps(filtered, cls=CustomEncoder)),
        media_type="application/json"
    )


@app.get("/api/fields")
def list_fields(path: str = Query(..., description="Path to JSON file")):
    abs_path = get_abs_path(path)

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(
        content=json.loads(json.dumps(data, cls=CustomEncoder)),
        media_type="application/json"
    )


@app.post("/api/field")
def create_field(added_field: Field,
                 path: str = Query(..., description="Path to JSON file"),
                 parent_path: str = Query(..., description="field belong to which parent field")
    ):
    abs_path = get_abs_path(path)
    field_loader = FieldLoader(BASE_PATH, abs_path)
    fields = field_loader.load_fields_to_dict()
    parent = field_loader.find_field_by_path(fields, parent_path)
    if parent is None:
        if field_loader.is_key_exists(fields, added_field.key):
            raise HTTPException(status_code=409, detail=f'{added_field.key} already exists')
        fields.append(added_field)
    else:
        if field_loader.is_key_exists2(parent.children, added_field.key):
            raise HTTPException(status_code=409, detail=f'{added_field.key} already exists')
        parent.children.append(added_field)
    save_json(abs_path, fields)
    return added_field


@app.delete("/api/field")
def delete_field(target: Field,
                 path: str = Query(..., description="Path to JSON file"),
                 parent_path: str = Query(..., description="field belong to which parent field")
                 ):
    abs_path = get_abs_path(path)
    field_loader = FieldLoader(BASE_PATH, abs_path)
    fields = field_loader.load_fields_to_dict()
    parent = field_loader.find_field_by_path(fields, parent_path)
    if parent is None:
        parent_field = fields
    else:
        parent_field = field_loader.find_field_by_path(fields, parent_path)

    if isinstance(parent_field, list):
        parent_field[:] = [f for f in parent_field if f.key != target.key]
    else:
        parent_field.children = [f for f in parent_field.children if f.key != target.key]

    save_json(abs_path, fields)
    return target


@app.get("/api/fields/parents")
def get_parent_fields(path: str = Query(..., description="Path to JSON file")):
    abs_path = get_abs_path(path)
    field_loader = FieldLoader(BASE_PATH, abs_path)
    fields = field_loader.load_fields_to_dict()
    all_expends_field = field_loader.get_all_fields(fields)
    available_parent_fields = FieldLoader.get_available_parent_fields(all_expends_field)
    return available_parent_fields


@app.post("/api/file")
def create_file_or_folder(file: PrecheckFile, path: str = Query("", description="Relative folder path")):
    safe_path = os.path.abspath(os.path.join(BASE_PATH, path.strip("/")))

    if not safe_path.startswith(os.path.abspath(BASE_PATH)):
        raise HTTPException(status_code=403, detail="Access denied")

    full_path = os.path.join(
        safe_path,
        f"{file.name}.json" if file.file_type == FileType.FILE else file.name
    )

    try:
        if os.path.exists(full_path):
            raise HTTPException(status_code=409, detail=f'{file.file_type} ({file.name}) already exists')

        if file.file_type == FileType.FILE:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)
        elif file.file_type == FileType.FOLDER:
            os.makedirs(full_path, exist_ok=True)
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

        return JSONResponse(content={"message": "Created"}, status_code=201)

    except Exception as e:
        return APIResponse.internal_error(str(e))


@app.delete("/api/file")
def delete_file_or_folder(path: str = Query(..., description="Path to delete")):
    abs_path = get_abs_path(path)
    # 檔案是否存在
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="File or folder not found")

    try:
        if os.path.isfile(abs_path):
            os.remove(abs_path)
        elif os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            raise HTTPException(status_code=404, detail="Unknown file type")

        return JSONResponse(content={"message": "Deleted successfully"}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        # 其他未預期錯誤統一 500
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")

# uvicorn main:app --reload --host 0.0.0.0 --port 5000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
