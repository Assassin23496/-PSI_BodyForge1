from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from ..container import profile_repository
from ..utils.security import JWT_SECRET_KEY, JWT_ALGORITHM

# Оба источника токена доступны для Swagger:
# 1) OAuth2 Password Flow (модалка с username/password)
# 2) Ручной Bearer токен (вставка готового токена)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)  # без ведущего слеша и без авто-ошибки
bearer_scheme = HTTPBearer(auto_error=False)

def _unauthorized(detail: str = "Invalid or expired token") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

async def get_current_user(
    oauth2_token: str | None = Depends(oauth2_scheme),
    bearer_creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """
    Пробуем сначала взять токен из Bearer (если Swagger вставляет его вручную),
    иначе пробуем токен, пришедший из OAuth2 password flow.
    """
    token: str | None = None
    if bearer_creds and bearer_creds.scheme.lower() == "bearer":
        token = bearer_creds.credentials
    elif oauth2_token:
        token = oauth2_token

    if not token:
        raise _unauthorized("Not authenticated")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise ValueError("No sub in token")
        profile_id = int(sub)
    except (JWTError, ValueError):
        raise _unauthorized("Invalid or expired token")

    user = await profile_repository.get_profile(profile_id)
    if user is None or not getattr(user, "is_active", True):
        raise _unauthorized("Account not found or inactive")

    return user


ADMIN_EMAIL = "admin@gmail.com"

async def require_admin(current_user=Depends(get_current_user)):
    # Профиль из базы (есть email)
    if current_user.email.strip().lower() != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user
