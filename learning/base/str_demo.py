if __name__ == '__main__':
    s = " Python 字符串处理 "
    print(s.strip())  # 去除两端空格
    print(s.lstrip())  # 去除左端空格
    print(s.rstrip())  # 去除右端空格
    print(s.replace(" ", ""))

    ens = "Hello Python"
    print(ens.upper())  # 全大写
    print(ens.lower())  # 全小写
    print(ens.capitalize())  # 仅句首大写
    print(ens.title())  # 首字母大写
    print(ens*3) # 重复打印字符串多次

    # 对齐操作
    s_align = "Python"
    print(s_align.ljust(20, "-"))  # 左对齐
    print(s_align.rjust(20, "*"))  # 右对齐
    print(s_align.center(20, "-"))  # 中间对齐

    s = "Python是一门优雅的语言，Python非常适合初学者"
    # 查找子串的位置
    print(s.find("Python"))
    print(s.find("Python", 5))
    print(s.rfind("Python"))
    # 检查子串是否存在
    print("Python" in s)

    # 统计子串出现的次数
    print(s.count("Python"))

    # 判断字符类型
    s1 = "123456"
    s2 = "Python123"
    s3 = "python"
    s4 = "Python"
    print(s1.isdigit())  # 判断是否全是数字
    print(s2.isalnum())  # 判断是否全是数组或者是英文字符
    print(s3.islower())  # 判断是否都是小写
    print(s4.istitle())  # 判断是否都是首字母大写

    # 判断开头和结尾
    s_url = "https://www.python.org"
    print(s_url.startswith("http://"))
    print(s_url.startswith("https:/"))
    print(s_url.endswith("python"))
    print(s_url.endswith("org"))

    # 编码和解码
    s = "Python字符串处理"
    byte_s = s.encode("utf-8")
    print(byte_s)
    print(byte_s.decode("utf-8"))

    # 多行文本处理
    multi_line = """第一行文本
    第二行文本

    第四行文本（中间有空行）
    第五行文本"""
    lines = multi_line.splitlines()
    print(lines)
    print([line.strip() for line in lines if line.strip()])

    # 格式化多行文本
    name = "张三"
    score = 98
    report = f"""
    学生成绩报告
    ------------
    姓名：{name}
    语文成绩：{score}分
    评价：{'优秀' if score >= 90 else '良好'}
    """
    print(report)
