from learning.decorators import log_record


def fibonacci(n: int):
    a, b = 0, 1
    count = 0
    for _ in range(n):
        yield a
        a, b = b, a + b
        count += 1

@log_record
def generate_user_data(total: int):
    for i in range(total):
        yield {
            "id": i,
            "age": 20 + i,
            "name": f"user_{i}",
            "city": "beijing" if i % 2 == 0 else "shanghai",
            "income": 5000 + i * 100
        }


if __name__ == '__main__':
    # 生成器表达式
    odd_square_gen = (x ** 2 for x in range(10) if x % 2 == 1)
    print("-".join([str(num) for num in odd_square_gen]))

    # 自定义生成函数
    fib_gen = fibonacci(10)
    print("*".join(str(num) for num in fib_gen))

    # 自定义链式生成器
    user_gen = generate_user_data(20)
    filtered_gen = (user for user in user_gen if user["city"] == "beijing" and user["income"] > 5500)
    total_income = 0
    count = 0
    for user in filtered_gen:
        print(user["age"], user["name"], user["city"], user["income"])
        total_income += user["income"]
        count += 1
    average_income = total_income / count
    print(f"average income: {average_income:.2f}")
