# 自定义迭代器
class NumberIterator:
    def __init__(self, max_num: int):
        self.max_num: int = max_num
        self.current: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.max_num:
            self.current += 1
            return self.current
        # 没有元素时抛异常，告诉程序“遍历结束”
        raise StopIteration


if __name__ == '__main__':
    # 列表转迭代器
    list = [1, 2, 3]
    iter_list = iter(list)
    print(next(iter_list))
    print(next(iter_list))
    print(next(iter_list))

    # 自定义迭代器
    num_iter = NumberIterator(10)
    for number in num_iter:
        print(number)
