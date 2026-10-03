import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

def main():
    print("Виконання  Завдання 2")

from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

users = {
    "ai_security_expert": {
        "role": "ai_security",
        "clearance": 4,
        "department": "AI Security",
        "active": True,
    },
    "ml_engineer": {
        "role": "ml_engineer",
        "clearance": 3,
        "department": "Machine Learning",
        "active": True,
    },
    "data_engineer": {
        "role": "data_engineer",
        "clearance": 2,
        "department": "Data Engineering",
        "active": True,
    },
    "research_assistant": {
        "role": "researcher",
        "clearance": 2,
        "department": "Research",
        "active": True,
    },
    "training_bot": {
        "role": "bot_account",
        "clearance": 1,
        "department": "Automation",
        "active": False,
    },
}

resources = [
    ("ai_models", 4),
    ("training_datasets", 3),
    ("data_pipelines", 2),
    ("research_notebooks", 2),
    ("model_artifacts", 4),
    ("synthetic_data", 1),
    ("adversarial_tests", 3),
    ("model_registry", 4),
    ("feature_stores", 2),
    ("public_models", 1),
]

security_levels = (
    "Open Source",
    "Internal Research",
    "Proprietary",
    "Trade Secret",
)

blocked_users = ("training_bot", "model_theft", "data_poisoning_acc")



print("Ресурси/рівень допуку")
for res_name,req_level in resources:
    level_name = security_levels[req_level-1]
    print(f"{res_name}/ {level_name}")

def check_access(user_key: str, req_clearance: int) -> tuple[bool, str]:
    if user_key not in users:
        return False, "користувача не знайдено"

    user_info = users[user_key]

    if user_key in blocked_users or not user_info["active"]:
        return False, "Заблоковано/неактивно"

    if user_info["clearance"] >= req_clearance:
        return True,  "Дозволено"
    if user_info["clearance"] < req_clearance:
         return  False, "Недостатньо прав"


if __name__ == "__main__":
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print(f"{'Користувач'} / {'Ресурс'} / {'Статус'} / {'причіна відмови'}")

    for user_key in users:
        for res_name, req_level in resources:
            allowed, status_msg = check_access(user_key, req_level)
            access_str = "allow" if allowed else "DENy"

            print( f"{user_key} / {res_name} / {access_str} / {status_msg}")
