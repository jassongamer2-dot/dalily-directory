import jwt
from fastapi import Depends, HTTPException, Header
from app.config import settings
from app.database import get_pool

_jwks_client = jwt.PyJWKClient(
    f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json")


async def get_current_user(authorization: str = Header(...)) -> dict:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token or token == "undefined":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as e:
        print(f"JWT verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_org_id(user: dict = Depends(get_current_user)) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT organization_id FROM user_profiles WHERE id = $1", user["sub"])
    if not row:
        raise HTTPException(
            status_code=403, detail="No organization membership found")
    return str(row["organization_id"])
