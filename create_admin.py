from database import SessionLocal
import models
from routers.auth_utils import hash_password   # ✅ import this

db = SessionLocal()

admin = models.User(
    username="admin",
    password=hash_password("admin123"), 
    role="admin"
)

db.add(admin)
db.commit()

print("Admin created!")