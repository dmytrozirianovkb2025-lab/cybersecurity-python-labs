import os
import random
import sys

sys.path.append( os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def main():
    print("Виконання  Завдання 1")

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

passwords = [
    "C0mpli4nc3Ch3ck",
    "weak",
    "R1skAss3ssm3nt",
    "guest",
    "Vulner4bilitySc4n",
    "temp",
    "P3netrat10nT3st",
    "demo",
    "S3curityAud1t",
    "trial",
]
criteria = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

forbidden_passwords = {"weak", "guest", "temp", "demo", "trial", "password"}

for _ in range(3):
    used_pass =random.choice(passwords)
    passwords.append(used_pass)

def evaluate_password(password, passwords_list, crit, forbidden):
    if password in forbidden or len(password) < crit["min_length"]:
        return "Заборонений / Дуже слабкий"

    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_special = any(not c.isalnum() for c in password)


    all_criteria_met = has_digit and has_upper and has_special
    is_unique = passwords_list.count(password) == 1

    if all_criteria_met and len(passwords) >= crit["min_length"] + 4  and is_unique:
        return "дуже сильний"
    elif all_criteria_met:
        return "сильний"
    elif has_digit or has_upper or has_special:
        return "середній"
    else:
        return "дуже слабкий"
if __name__ == "__main__":
    print(f"Студент {STUDENT_NAME}, Група {GROUP_NAME}, Варіант{VARIANT_NUMBER}")
    print(r"Пароль/ Стійкість")
    for pswd in passwords:
        status = evaluate_password(pswd, passwords, criteria, forbidden_passwords)
        print(f"{pswd}: {status}")








