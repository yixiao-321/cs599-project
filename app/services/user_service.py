import hashlib
from sqlalchemy.orm import Session
from app.models.database import User

def md5_hash(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def create_user(db: Session, username: str, password: str, name: str = None, email: str = None):
    password_hash = md5_hash(password)
    user = User(
        username=username,
        password_hash=password_hash,
        name=name,
        email=email
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def verify_password(db: Session, username: str, password: str) -> bool:
    user = get_user_by_username(db, username)
    if not user:
        return False
    return user.password_hash == md5_hash(password)

def init_default_users(db: Session):
    default_users = [
        {"username": "admin", "password": "123456", "name": "管理员", "email": "admin@example.com"},
        {"username": "zhangsan", "password": "123456", "name": "张三", "email": "zhangsan@example.com"},
        {"username": "lisi", "password": "123456", "name": "李四", "email": "lisi@example.com"}
    ]
    
    for user_data in default_users:
        existing_user = get_user_by_username(db, user_data["username"])
        if not existing_user:
            create_user(db, **user_data)