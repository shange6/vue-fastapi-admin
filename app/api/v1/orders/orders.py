import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.settings.config import settings
from app.schemas.base import Success
from app.utils.dwg2dxf import dwg2dxf, dxf2dict

router = APIRouter()

@router.post("/file", summary="文件上传")
async def upload_single_file(file: UploadFile = File(...)):
    try:
        # 1. 检查配置
        upload_config = settings.UPLOAD_CONFIG
        upload_dir = settings.UPLOAD_DIR
        
        # 确保上传目录存在
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 2. 校验文件类型
        if file.content_type not in upload_config["ALLOWED_TYPES"]:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型，仅允许：{', '.join(upload_config['ALLOWED_TYPES'])}"
            )

        # 3. 读取文件内容并校验大小
        content = await file.read()
        if len(content) > upload_config["MAX_SIZE"]:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大 {upload_config['MAX_SIZE']//1024//1024}MB）"
            )
        
        # 4. 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[-1]
        file_name = f"{upload_config['FILE_NAME_PREFIX']}{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, file_name)

        # 5. 保存文件
        with open(file_path, "wb") as f:
            f.write(content)

        # 6. 返回结果
        # 静态文件服务的挂载点为 /uploads
        file_url = f"/uploads/{file_name}"

        return Success(
            msg="文件上传成功",
            data=dxf2dict(dwg2dxf(file_path))
                # "file_name": file.filename,
                # "save_name": file_name,
                # "file_path": file_path,
                # "file_url": file_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", summary="工单列表")
async def list_task_order(
        page: int = Query(1, description="页码"),
        page_size: int = Query(10, description="每页数量"),
    ):
    pass