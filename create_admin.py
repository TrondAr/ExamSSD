from database import get_user_by_email, create_user
from security import hash_password

email = "admin1@GPapp.com"
password = "smekkL0bb!!!"
if not get_user_by_email(email):
    create_user(email, hash_password(password), role="admin")
    print("Admin created:", email)
else:
    print("Admin already exists")
