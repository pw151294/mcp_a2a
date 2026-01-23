from operator import itemgetter

if __name__ == '__main__':
    d = {'apple': 10, 'orange': 20, 'banana': 5, 'rotten tomato': 1}
    for item in d.items():
        print(item)
    print(sorted(d, key=d.get))  # 对字段元素按照值排序
    print(sorted(d.items(), key=lambda x: x[1]))  # 对字段元素按照值排序
    print(sorted(d.items(), key=itemgetter(1)))  # 对字段元素按照值排序，等同于上面

    d1 = {'a': 1, 'b': 3}
    d2 = {'b': 2, 'c': 4}
    d.update(d1)
    print(d)
    d.update(d2)
    print(d)

    print({**d1, **d2})  # 合并字典，d2的值会覆盖d1中相同key的值
    print(dict(d1.items() | d2.items()))  # 合并字典，d2的值会覆盖d1中相同key的值
    d1.update(d2)  # 合并字典，d2的值会覆盖d1中相同key的值
    print(d1)

    # 从字典中删除元素
    del d1['a']
    del d2['b']
    print({**d1, **d2})
    print(dict(d1.items() | d2.items()))


