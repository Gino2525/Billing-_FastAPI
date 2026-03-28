from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models, schemas
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from jose import JWTError, jwt
from routers import auth, user, products, billing
from fastapi.staticfiles import StaticFiles
from routers.user import get_current_user
import os, sys
import webbrowser
from routers.auth_utils import hash_password

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(billing.router)

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/dashboard",response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/invoice/{bill_id}", response_class=HTMLResponse)
def invoice_page(request: Request, bill_id: int):
    return templates.TemplateResponse("invoice.html", {
        "request": request,
        "bill_id": bill_id
    })

@app.on_event("startup")
def startup():
    print("Server starting...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.username == "admin").first()

        if not admin:
            admin_user = models.User(
                username="admin",
                password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("Admin created!")
        else:
            print("Admin already exists")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn

    print("Starting FastAPI server...")

    webbrowser.open("http://localhost:8000")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )