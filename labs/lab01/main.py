import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

print(f"Лабораторна робота №1  Виконав: {STUDENT_NAME}, група {GROUP_NAME}")
print(f"Варіант №{VARIANT_NUMBER}\n")

from labs.lab01 import task1, task2, task3

def main() -> None:
    print(f"Лабораторна робота №1  Виконав: {STUDENT_NAME}, група {GROUP_NAME}")
    print(f"Варіант №{VARIANT_NUMBER}\n")

    print("\nЗавдання 1")
    task1.main()

    print("\nЗавдання 2")
    task2.main()

    print("\nЗавдання 3")
    task3.main()


if __name__ == "__main__":
    main()