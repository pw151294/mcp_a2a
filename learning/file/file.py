# 读取错误日志
def read_log(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            yield line.strip()


def filter_error(log_lines):
    return (line for line in log_lines if 'error' in line.lower())


def extract_timestamps(error_lines):
    return (line.split(' ')[0] for line in error_lines)


class FileReader:
    """文件读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file = None

    def __enter__(self):
        """进入with块时执行，返回连接对象"""
        self.file = open(self.file_path, 'r', encoding='utf-8')
        return self.file

    def __exit__(self):
        """退出with块时执行，关闭连接"""
        if self.file is not None:
            self.file.close()


if __name__ == '__main__':
    log_path = "large_log.txt"
    log_gen = read_log(log_path)
    error_gen = filter_error(log_gen)
    timestamp_gen = extract_timestamps(error_gen)
    for ts in timestamp_gen:
        print(ts)

    with FileReader(log_path) as file:
        print(file.read())