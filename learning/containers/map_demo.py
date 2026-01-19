from multiprocessing.pool import worker


def upper(s: str) -> str:
    return s.upper()


def lower(s: str) -> str:
    return s.lower()


if __name__ == "__main__":
    words = ['sentence', 'fragment']

    upper_words = [upper(word) for word in words]
    print(upper_words)
    lower_words = [lower(word) for word in words]
    print(lower_words)

    upper_list = list(map(upper, words))
    print(upper_list)
    lower_list = list(map(lower, words))
    print(lower_list)

    # 将两个列表转换成字典
    list1 = ['karl', 'lary', 'keera']
    list2 = [28934, 28935, 28936]
    dict0 = dict(zip(list1, list2))
    print(dict0)
    dict1 = {k: v for k, v in zip(list1, list2)}
    print(dict1)
    dict2, tuples = {}, zip(list1, list2)
    for (k, v) in tuples:
        if k in dict2:
            pass
        else:
            dict2[k] = v
    print(dict2)

