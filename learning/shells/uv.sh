uv venv
uv python install 3.11 3.12
uv python list
uv venv --python 3.12
source .venv/bin/activate
deactivate

# 依赖管理
uv init project_name # 初始化项目
uv add -i https://pypi.tuna.tsinghua.edu.cn/simple pandas
uv add package_name
uv remove package_name
uv update package_name
uv export -o requirements.txt
uv sync # 根据 pyproject.toml 或 requirements.txt 安装所有依赖
uv sync --frozen --extra=dev # 严格按锁文件 uv.lock 安装，包括开发依赖
