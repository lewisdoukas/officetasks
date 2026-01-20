import os
import getpass
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db, User, Rank

def main():
    app = create_app()
    with app.app_context():
        last_name = input("Admin last name (used as username): ").strip()
        first_name = input("Admin first name: ").strip()
        rank_str = input("Rank: ").strip().lower()
        internal_phone = input("Internal phone (optional): ").strip() or None
        mobile_phone = input("Mobile phone (optional): ").strip() or None

        if rank_str not in {r.value for r in Rank}:
            raise SystemExit(f"Invalid rank: {rank_str}")

        pw = getpass.getpass("Admin password: ")
        pw2 = getpass.getpass("Confirm password: ")
        if pw != pw2:
            raise SystemExit("Passwords do not match.")

        existing = User.query.filter_by(last_name=last_name).first()
        if existing:
            raise SystemExit("A user with that last name already exists (login uses last name).")

        u = User(
            rank=Rank(rank_str),
            first_name=first_name,
            last_name=last_name,
            internal_phone=internal_phone,
            mobile_phone=mobile_phone,
            active=True,
            is_admin=True,
            password_hash=generate_password_hash(pw),
        )
        db.session.add(u)
        db.session.commit()
        print(f"Created admin user id={u.id}")

if __name__ == "__main__":
    main()
