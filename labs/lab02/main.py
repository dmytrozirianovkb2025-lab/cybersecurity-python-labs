import os
import sys
import time

# Додаємо шлях до кореневої папки проєкту, щоб Python бачив всі модулі
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from labs.lab02.task1 import Admin, AuditLog, User, UserAccount
from labs.lab02.task2 import main as run_task2


def run_demo() -> None:
    print("lab02")
    audit_log = AuditLog()



    print(" 1. Аутентифікація (Успішний та невдалий вхід)")
    user = User(username="dima123", email="dima@gmail.com")
    user.set_password("SecretPass2026!")

    account = UserAccount(user=user, audit_log=audit_log)


    fail_res = account.login(username="dima123", password="WrongPassword!", ip="192.168.1.10")
    print(f"Вхід з неправильним паролем: {fail_res}")


    success_res = account.login(username="dima123", password="SecretPass2026!", ip="127.0.0.1")
    print(f" Вхід з правильним паролем: {success_res}")
    print(f" Статус авторизації: {account.is_authenticated()}\n")


    print("2. Зміна email та RegEx валідація ")
    print(f"Поточний email: {user.email}")


    user.email = "new_dima@lpnu.ua"
    print(f" Email успішно змінено на: {user.email}")


    try:
        user.email = "dima123dqr"
    except ValueError as e:
        print(f"Перехоплено помилку валідації: {e}\n")


    print("3. Права адміністратора")
    admin = Admin(
        username="admin",
        email="admin@cyber.ua",
        permissions=["read_logs", "delete_users"],
    )
    print(f"Створено адміна: {admin}")

    admin.grant_permission("manage_roles")
    print(f"Після надання 'manage_roles': {admin.permissions}")

    admin.revoke_permission("delete_users")
    print(f"[Після вилучення 'delete_users': {admin.permissions}")
    print(f"Перевірка права 'read_logs': {admin.has_permission('read_logs')}\n")


    print("4. Вихід із системи")
    account.logout()
    print(f"Користувач вийшов. Авторизований: {account.is_authenticated()}\n")

    print(" 5. Таймаут сесії (Session Timeout) ")
    account.login(username="dima123", password="SecretPass2026!", ip="10.0.0.1")
    print(f"Сесію створено. Авторизований: {account.is_authenticated()}")

    print("Імітація паузи у 2 секунди...")
    time.sleep(2)


    is_active_after_timeout = account.session.is_active(timeout_sec=1)
    print(f" Чи дійсна сесія після таймауту у 1 сек?: {is_active_after_timeout}\n")


    print(" 6. Записи AuditLog ")
    audit_log.show_all()



if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "scan":

        sys.argv = [sys.argv[0]] + sys.argv[2:]
        run_task2()
    else:

        print("python3 -m labs.lab02.main demo task1")
        print("  python -m labs.lab02.main scan --scan-dir labs/lab02/data_v13 --mask # Запуск Task 2")
