# 使用launchd后台服务方式（推荐）
brew services start rabbitmq

# 使用命令行方式启动
rabbitmq-server -detached

# 查看状态
brew services list | grep rabbitmq
# 或
rabbitmqctl status

# 停止服务
brew services stop rabbitmq
# 或
rabbitmqctl stop

# 启用Web管理界面
rabbitmq-plugins enable rabbitmq_management

# 查看现有用户
rabbitmqctl list_users