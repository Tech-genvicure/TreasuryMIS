from getpass import getpass

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


def main():
    username = input("Enter username: ").strip()

    if not username:
        raise ValueError("Username cannot be empty.")

    password = getpass("Enter password: ")

    if not password:
        raise ValueError("Password cannot be empty.")

    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        raise ValueError("Passwords do not match.")

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_user:
            print(f"User '{username}' already exists.")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            is_active=True,
        )

        db.add(user)
        db.commit()

        print(f"User '{username}' created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()