import uvicorn
from uvicorn.config import LOGGING_CONFIG
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

# 初始化 FastAPI 应用，关闭默认的 docs 自动加载
app = FastAPI(docs_url=None, redoc_url=None)

# 挂载本地静态资源目录（swagger-ui 静态文件）
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# 自定义 Swagger UI 页面
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        # 指向本地 Swagger UI 资源（替代 CDN）
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/favicon-32x32.png",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    )

# 配置 OAuth2 重定向（可选，若无 OAuth2 可忽略）
# @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
# async def swagger_ui_redirect():
#     return get_swagger_ui_oauth2_redirect_html()

# 你的其他路由（如之前的上传接口）
# from app.routers import upload
# app.include_router(upload.router)

if __name__ == "__main__":
    # 修改默认日志配置
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"][
        "fmt"
    ] = '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s'
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

    uvicorn.run("app:app", host="0.0.0.0", port=9999, reload=True, log_config=LOGGING_CONFIG)
