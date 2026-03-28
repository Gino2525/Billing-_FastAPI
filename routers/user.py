from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import SessionLocal
import models
from .auth_utils import hash_password, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

router = APIRouter(prefix="/users", tags=["Users"])

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    print("🔥 AUTH FUNCTION CALLED")

    token = credentials.credentials
    print("🔑 TOKEN:", token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("📦 PAYLOAD:", payload)

        username = payload.get("sub")
        print("👤 USERNAME FROM TOKEN:", username)

        user = db.query(models.User).filter(models.User.username == username).first()
        print("🧾 DB USER:", user)

        if not user:
            print("❌ USER NOT FOUND IN DB")
            raise HTTPException(status_code=401, detail="User not found")

        print("✅ AUTH SUCCESS")
        return user  

    except JWTError as e:
        print("❌ JWT ERROR:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/create")
def create_user(
    user: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create users")

    if user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot be created via API")

    existing = db.query(models.User).filter(models.User.username == user["username"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user["username"],
        password=hash_password(user["password"]),
        role=user["role"]
    )

    db.add(new_user)
    db.commit()

    return {"msg": "User created successfully"}

@router.get("/admin")
def admin_dashboard(current_user: dict = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    return {"msg": "Welcome Admin"}


@router.post("/register")
def register(user: dict, db: Session = Depends(get_db)):

    
    if "role" in user:
        raise HTTPException(status_code=403, detail="Cannot set role manually")
 
    existing = db.query(models.User).filter(models.User.username == user["username"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user["username"],
        password=hash_password(user["password"]),
        role="staff"
    )

    db.add(new_user)
    db.commit()

    return {"msg": "User registered successfully"}


@router.get("/")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    users = db.query(models.User).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role
        }
        for u in users
    ]

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    db.delete(user)
    db.commit()

    return {"msg": "User deleted successfully"}