import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from .db import get_session
from .models import AdminUser, AppSettings, AuditLog

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    with get_session() as db:
        user = db.exec(select(AdminUser).where(AdminUser.username == username)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user

def get_setting(key: str) -> str:
    """Get setting value from database"""
    with get_session() as db:
        setting = db.exec(select(AppSettings).where(AppSettings.key == key)).first()
        return setting.value if setting else None

def set_setting(key: str, value: str, description: str = None, user_id: int = None):
    """Set setting value in database"""
    with get_session() as db:
        setting = db.exec(select(AppSettings).where(AppSettings.key == key)).first()
        old_value = setting.value if setting else None
        
        if setting:
            setting.value = value
            setting.description = description
            setting.updated_at = datetime.utcnow()
            setting.updated_by = user_id
            action = "setting_update"
        else:
            setting = AppSettings(
                key=key,
                value=value,
                description=description,
                updated_by=user_id
            )
            db.add(setting)
            action = "setting_create"
        
        db.commit()
        db.refresh(setting)
        
        # Log the change if user_id is provided
        if user_id:
            log_audit_event(
                user_id=user_id,
                action=action,
                resource_type="setting",
                resource_id=key,
                old_value=old_value,
                new_value=value
            )
        
        return setting

def log_audit_event(
    user_id: int = None,
    username: str = None,
    action: str = None,
    resource_type: str = None,
    resource_id: str = None,
    old_value: str = None,
    new_value: str = None,
    ip_address: str = None,
    user_agent: str = None,
    details: str = None
):
    """Log an audit event to the database"""
    with get_session() as db:
        # Get username if not provided but user_id is
        if not username and user_id:
            user = db.exec(select(AdminUser).where(AdminUser.id == user_id)).first()
            username = user.username if user else "unknown"
        
        audit_log = AuditLog(
            user_id=user_id,
            username=username or "system",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log
