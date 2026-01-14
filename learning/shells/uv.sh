uv venv
uv venv --python 3.12
source .venv/bin/activate
deactivate

# 依赖管理
uv add package_name
uv remove package_name
uv update package_name
uv sync # 根据 pyproject.toml 或 requirements.txt 安装所有依赖
uv sync --frozen --extra=dev # 严格按锁文件 uv.lock 安装，包括开发依赖
