from collections import Counter
from functools import reduce  # 使用标准库的 reduce

if __name__ == '__main__':
    a = [1, 2, 3, 1, 2, 3, 2, 2, 4, 5, 1]
    print(set(a))
    print(max(set(a)))
    print(max(set(a), key=a.count))  # 出现次数最多的元素

    print(Counter(a))  # 统计每个元素出现的次数
    print(Counter(a).most_common(2))  # 出现次数最多的前
    s1, s2 = 'abc', 'cba'
    print(Counter(s1) == Counter(s2))  # 判断两个字符串是否由相同字符组成

    s = 'abcdefghijklmnopqrstuvwxyz'
    print(s[::-1])  # 字符串反转
    n = 123456789
    print(int(str(n)[::-1]))  # 整数反转
    print(a[::-1])  # 列表反转

    # 使用zip函数
    original = [['a', 'b'], ['c', 'd'], ['e', 'f']]
    transposed = zip(*original)  # 转置二维数组
    print(list(transposed))
    maths = [59, 64, 75, 86]
    physics = [78, 98, 56, 56]
    total = [x + y for (x, y) in zip(maths, physics)]
    print(total)
    print(dict(enumerate(total)))

    lst = [40, 10, 20, 30, 20, 50, 30, 20]
    print(min(range(len(lst)), key=lst.__getitem__))  # 返回最小值的索引
    print(max(range(len(lst)), key=lst.__getitem__))  # 返回最大值的索引

    print(list(set(lst)))  # 去重但不保证顺序
    print(sorted(set(lst), key=lst.index))  # 去重并保持顺序

    print(sum([i for i in range(100) if i % 2 == 0]))  # 计算0-99之间所有偶数的和

    # 列表推导式
    print([i ** 2 for i in range(1, 100) if i % 2 == 1])  # 1-99之间所有奇数的平方列表
    # 嵌套推导
    print([ch for row in original for ch in row])  # 将二维数组展开为一维数组

    # 使用.sort()函数对list排序
    shuffle_list = [40, 10, 20, 30, 20, 50, 30, 20]
    shuffle_list.sort(reverse=True)
    print(shuffle_list)
    shuffle_list.sort(reverse=False)
    print(shuffle_list)

    # 使用内置的sorted关键字对list排序
    shuffle_list = [40, 10, 20, 30, 20, 50, 30, 20]
    sorted_list = sorted(shuffle_list)
    print(sorted_list)
    sorted_list = sorted(shuffle_list, reverse=True)
    print(sorted_list)

    # 使用map、filter还有reduce函数
    lst = [40, 10, 20, 30, 20, 50, 30, 20]
    # 每个元素乘以2
    two_times_list = list(map(lambda x: x * 2, lst))
    print(two_times_list)
    # 过滤出所有3的倍数
    three_times_list = list(filter(lambda x: True if x % 3 == 0 else False, lst))
    print(three_times_list)
    # 使用标准库 reduce 计算所有元素之和
    total_sum = reduce((lambda x, y: x + y), three_times_list)
    print(total_sum)
