import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

PBKDF2_ITERATIONS = 100000
SESSION_TIMEOUT_SEC = 900


class User:
    def __init__(self, username: str, email: str, role: str = "user", active: bool = True) -> None:
        self.username = username
        self.email = email
        self.role = role
        self.active = active
        self._password_hash: bytes | None = None
        self._password_salt: bytes | None = None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str) -> None:
        pattern = r"^[a-zA-Z][a-zA-Z0-9._%+-]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValueError(f"Invalid email address: {email}")
        self._email = email

    def set_password(self, password: str) -> None:
        self._password_salt = os.urandom(16)
        self._password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self._password_salt,
            PBKDF2_ITERATIONS,


        )

    def check_password(self, password: str) -> bool:
        if not self._password_hash or not self._password_salt:
            return False

        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self._password_salt,
            PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(self._password_hash, computed_hash)

    def deactivate(self) -> None:
        self.active = False

    def __str__(self) -> str:
        return f"User(username: {self.username}, email: {self.email}, role: {self.role})"


class Admin(User):
    def __init__(
        self,
        username: str,
        email: str,
        permissions: list[str] | set[str] | None = None,
        role: str = "admin",
        active: bool = True,
    ) -> None:
        super().__init__(
            username=username,
            email=email,
            role=role,
            active=active,
        )
        self.permissions: set[str] = set(permissions) if permissions else set()

    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        base_str = super().__str__()
        perms = ",".join(sorted(self.permissions)) if self.permissions else "None"
        return f"{base_str} (Permissions: {perms})"


class Session:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        now = datetime.now(timezone.utc)
        self.login_time = now
        self.last_activity = now

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("Timeout повинен бути додатнім")
        now = datetime.now(timezone.utc)
        return (now - self.last_activity) <= timedelta(seconds=timeout_sec)


@dataclass
class AuditRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self) -> None:
        self.logs: list[AuditRecord] = []

    def add_log(self, username: str, action: str) -> None:
        record = AuditRecord(
            timestamp=datetime.now(timezone.utc),
            username=username,
            action=action,
        )
        self.logs.append(record)

    def show_all(self) -> None:
        print("Audit Log Records:")
        for log in self.logs:
            time_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"{time_str} User: {log.username} | Action: {log.action}")


class UserAccount:
    def __init__(
        self,
        user: User,
        session: Session | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.user = user
        self.session = session
        self.audit_log = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        if self.user.username != username or not self.user.active:
            self.audit_log.add_log(username, "login_failure")
            return False

        if self.user.check_password(password):
            self.session = Session(ip=ip)
            self.session.touch()
            self.audit_log.add_log(username, "login_success")
            return True

        self.audit_log.add_log(username, "login_failure")
        return False

    def is_authenticated(self) -> bool:
        if self.session is None:
            return False
        return self.session.is_active(SESSION_TIMEOUT_SEC)

    def logout(self) -> None:
        if self.session is not None:
            username = self.user.username
            self.session = None
            self.audit_log.add_log(username, "logout")

    def __getitem__(self, key: str) -> str:
        allowed_keys = {"user", "session", "audit_log"}
        if key not in allowed_keys:
            raise KeyError(f"Ключ '{key}' недоступний.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: str) -> None:
        allowed_keys = {"user", "session", "audit_log"}
        if key not in allowed_keys:
            raise KeyError(f"Запис за ключем '{key}' заборонений.")

        if key == "user" and not isinstance(value, User):
            raise TypeError("Значення повинно бути екземпляром класу User.")
        if key == "session" and value is not None and not isinstance(value, Session):
            raise TypeError("Значення повинно бути екземпляром класу Session або None.")
        if key == "audit_log" and not isinstance(value, AuditLog):
            raise TypeError("Значення повинно бути екземпляром класу AuditLog.")

        setattr(self, key, value)