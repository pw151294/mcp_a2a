poetry init # 初始化项目
poetry install  # 安装项目依赖
poetry add requests # 安装依赖包
poetry shell # 进入虚拟环境
poetry remove requests # 卸载依赖包
poetry update requests # 更新依赖包
poetry show # 列出已安装的包
poetry show --outdated # 列出可更新的包
poetry lock # 生成或更新锁文件
poetry export -f requirements.txt --output=requirements.txt # 导出依赖到 requirements
