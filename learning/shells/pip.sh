pip --version
pip install package_name
pip install package==1.2.3
pip install --upgrade package
pip uninstall package
pip list
pip list --outdated # 列出可更新的包

pip freeze > requirements.txt
pip install -r requirements.txt
pip install package -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置pip的镜像源为清华大学源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# pyinstaller打包
pip install pyinstaller
pyinstaller --onefile script.py

# 构建pip包
python setup.py sdist bdist_wheel
twine upload dist/*
pip install dist/package_name-version-py3-none-any.whl