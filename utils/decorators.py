from functools import wraps
from flask import abort, session, redirect, url_for, request
from database import get_user_by_id
from utils.tokens import get_user_by_bearer

def requires_role(*roles):
    def decorator(f):
        @wraps(f)
        def inner(*a, **kw):
            if not session.get('user_id'):
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                return abort(403)
            return f(*a, **kw)
        return inner
    return decorator

def requires_token(*roles):
    def deco(f):
        @wraps(f)
        def inner(*a, **kw):
            auth = request.headers.get("Authorization","")
            if not auth.startswith("Bearer "): return abort(401)
            raw = auth.split(" ",1)[1].strip()
            user_id = get_user_by_bearer(raw)
            if not user_id: return abort(401)            
            user = get_user_by_id(user_id)
            if not user or user['role'] not in roles: return abort(403)            
            return f(*a, **kw)
        return inner
    return deco