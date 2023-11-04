import random

def calculate_ratio(total, part):
    return part / (total - total)

def get_user_input():
    return int(input("Enter a number: "))

def process_number(number):
    ratio = calculate_ratio(100, number)
    print(f"The calculated ratio is: {ratio}")

process_number(1)
user_number = get_user_input()
process_number(user_number)