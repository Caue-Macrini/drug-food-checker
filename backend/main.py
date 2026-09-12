import os, time, secrets, hashlib, hmac, json, logging, smtplib
from pathlib import Path
from collections import defaultdict, deque
from threading import Lock
from contextlib import asynccontextmanager
from email.message import EmailMessage
import bcrypt, jwt
from fastapi import FastAPI, Depends, HTTPException, Request, Response, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from models import Base, engine, Session, User, Profile, Consent, HistoryKey, History, Audit, Reset, Dataset, Drug, Food, now
from schemas import Signup, Login, ClinicalProfile, Check, EmailRequest, ResetRequest, PasswordRequest, AccountAction, ImportDataset
from services import uid, search_catalog, build_result, import_dataset

PRODUCTION = os.getenv('APP_ENV') == 'production'
SECRET = os.getenv('JWT_SECRET')
if not SECRET:
    if PRODUCTION:
        raise RuntimeError('JWT_SECRET obrigatório em produção')
    secret_path = Path('.local-secret')
    if not secret_path.exists():
        secret_path.write_text(secrets.token_hex(48))
    SECRET = secret_path.read_text().strip()
if len(SECRET) < 32:
    raise RuntimeError('JWT_SECRET deve ter pelo menos 32 caracteres')
ORIGIN = os.getenv('APP_ORIGIN', 'http://127.0.0.1:5173')
if PRODUCTION and not ORIGIN.startswith('https://'):
    raise RuntimeError('APP_ORIGIN deve usar HTTPS em produção')
COOKIE = 'dfc_session'
logger = logging.getLogger('drugfood')

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    with Session() as db:
        if not db.scalar(select(Dataset)) and os.getenv('SEED_DATA', 'true') == 'true':
            seed = Path(__file__).parent.parent / 'data' / 'starter.json'
            import_dataset(db, ImportDataset.model_validate_json(seed.read_text(encoding='utf-8')))
            db.commit()
    yield

app = FastAPI(title='Drug-Food Checker', version='1.0.0', lifespan=lifespan)
hits = defaultdict(deque)
hit_lock = Lock()

@app.middleware('http')
async def protections(request: Request, call_next):
    if request.url.path.startswith('/api'):
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            origin = request.headers.get('origin')
            if (origin and origin != ORIGIN) or request.headers.get('sec-fetch-site') == 'cross-site':
                return JSONResponse({'detail': 'Origem não permitida'}, status_code=403)
            if not request.headers.get('content-type', '').startswith('application/json'):
                return JSONResponse({'detail': 'Envie application/json'}, status_code=415)
            # Stream bound protects uploads even without Content-Length.
            size = 0
            body = []
            async for chunk in request.stream():
                size += len(chunk)
                if size > 8_000_000:
                    return JSONResponse({'detail': 'Limite de 8 MB por importação'}, status_code=413)
                body.append(chunk)
            request._body = b''.join(body)
        identity = request.client.host if request.client else 'local'
        group = 'auth' if '/auth/' in request.url.path else 'api'
        limit = 20 if group == 'auth' else 120
        stamp = time.monotonic()
        with hit_lock:
            for key in list(hits):
                if not hits[key] or stamp - hits[key][-1] > 60:
                    del hits[key]
            bucket = hits[(identity, group)]
            while bucket and stamp - bucket[0] >= 60:
                bucket.popleft()
            if len(bucket) >= limit:
                return JSONResponse({'detail': 'Muitas solicitações. Aguarde um minuto.'}, status_code=429, headers={'Retry-After':'60'})
            bucket.append(stamp)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    if request.url.path.startswith('/api'):
        response.headers['Cache-Control'] = 'no-store'
    if PRODUCTION:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def db_session():
    with Session() as db:
        yield db

def actor_hash(user_id):
    return hmac.new(SECRET.encode(), user_id.encode(), hashlib.sha256).hexdigest()

def audit(db, user_id, action):
    db.add(Audit(id=uid(), actor=actor_hash(user_id), action=action))

def public_user(user):
    return {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role, 'active': user.active, 'created_at': user.created_at}

def current_user(request: Request, db=Depends(db_session)):
    try:
        token = jwt.decode(request.cookies.get(COOKIE, ''), SECRET, algorithms=['HS256'], options={'require':['exp','sub','ver']})
        user = db.get(User, token['sub'])
        if not user or not user.active or user.token_version != token['ver']:
            raise ValueError()
        return user
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(401, 'Entre na sua conta para continuar')

def admin(user=Depends(current_user)):
    if user.role != 'admin':
        raise HTTPException(403, 'Acesso exclusivo da administração')
    return user

def set_session(response, user):
    token = jwt.encode({'sub': user.id, 'ver': user.token_version, 'iat': int(time.time()), 'exp': int(time.time()) + 3600 * 8}, SECRET, algorithm='HS256')
    response.set_cookie(COOKIE, token, httponly=True, secure=PRODUCTION, samesite='strict', max_age=3600 * 8, path='/')

def password_matches(password, hashed):
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False

DUMMY_HASH = bcrypt.hashpw(secrets.token_bytes(24), bcrypt.gensalt(rounds=12)).decode()

@app.get('/api/health')
def health(db=Depends(db_session)):
    datasets = db.scalars(select(Dataset).where(Dataset.active == True)).all()
    return {'status':'ok', 'datasets':[{'version':d.version, 'source':d.source, 'count':d.count} for d in datasets], 'mode':'educational', 'smtp_configured':bool(os.getenv('SMTP_HOST'))}

@app.post('/api/auth/register', status_code=201)
def register(data: Signup, response: Response, db=Depends(db_session)):
    user = User(id=uid(), name=data.name.strip(), email=data.email, password=bcrypt.hashpw(data.password.encode(), bcrypt.gensalt(rounds=12)).decode())
    db.add(user)
    try:
        db.flush()
        db.add_all([Profile(user_id=user.id, data={}), Consent(user_id=user.id)])
        audit(db, user.id, 'account.created.consent.v1')
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Não foi possível criar a conta com este e-mail')
    set_session(response, user)
    return public_user(user)

@app.post('/api/auth/login')
def login(data: Login, response: Response, db=Depends(db_session)):
    user = db.scalar(select(User).where(User.email == data.email))
    matched = password_matches(data.password, user.password if user else DUMMY_HASH)
    if not user or not matched or not user.active:
        raise HTTPException(401, 'E-mail ou senha inválidos')
    audit(db, user.id, 'session.login')
    db.commit()
    set_session(response, user)
    return public_user(user)

@app.post('/api/auth/logout')
def logout(response: Response, user=Depends(current_user), db=Depends(db_session)):
    user.token_version += 1
    db.commit()
    response.delete_cookie(COOKIE, path='/')
    return {'ok':True}

@app.post('/api/auth/forgot')
def forgot(data: EmailRequest, db=Depends(db_session)):
    user = db.scalar(select(User).where(User.email == data.email.strip().lower(), User.active == True))
    if user:
        token = secrets.token_urlsafe(32)
        db.execute(delete(Reset).where(Reset.user_id == user.id))
        db.add(Reset(token_hash=hashlib.sha256(token.encode()).hexdigest(), user_id=user.id, expires=int(time.time())+1800))
        link = f'{ORIGIN}/?reset={token}'
        try:
            if os.getenv('SMTP_HOST'):
                msg = EmailMessage()
                msg['Subject'] = 'Redefinir senha · Drug-Food Checker'
                msg['From'] = os.getenv('SMTP_FROM', 'noreply@localhost')
                msg['To'] = user.email
                msg.set_content(f'Use este link em até 30 minutos: {link}\nSe não solicitou, ignore esta mensagem.')
                with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.getenv('SMTP_PORT','1025')), timeout=10) as smtp:
                    if os.getenv('SMTP_TLS') == 'true':
                        smtp.starttls()
                    if os.getenv('SMTP_USER'):
                        smtp.login(os.environ['SMTP_USER'], os.environ['SMTP_PASSWORD'])
                    smtp.send_message(msg)
            elif not PRODUCTION:
                Path('outbox').mkdir(exist_ok=True)
                Path(f'outbox/{uid()}.txt').write_text(link, encoding='utf-8')
            else:
                raise RuntimeError('SMTP ausente')
            audit(db, user.id, 'password.reset.requested')
            db.commit()
        except Exception:
            db.rollback()
            logger.error('Falha no serviço de recuperação de senha')
    return {'message':'Se o e-mail estiver cadastrado, as instruções serão enviadas. Em desenvolvimento sem SMTP, consulte a pasta backend/outbox.'}

@app.post('/api/auth/reset')
def reset_password(data: ResetRequest, db=Depends(db_session)):
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    # Atomic delete-returning ensures reset tokens can only be consumed once.
    user_id = db.execute(delete(Reset).where(Reset.token_hash == token_hash, Reset.expires > int(time.time())).returning(Reset.user_id)).scalar_one_or_none()
    if not user_id:
        raise HTTPException(400, 'Link inválido ou expirado')
    user = db.get(User, user_id)
    user.password = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt(rounds=12)).decode()
    user.token_version += 1
    audit(db, user.id, 'password.reset.completed')
    db.commit()
    return {'message':'Senha atualizada. Entre com sua nova senha.'}

@app.get('/api/me')
def me(user=Depends(current_user)):
    return public_user(user)

@app.get('/api/profile')
def get_profile(user=Depends(current_user), db=Depends(db_session)):
    return db.get(Profile, user.id).data

@app.put('/api/profile')
def save_profile(data: ClinicalProfile, user=Depends(current_user), db=Depends(db_session)):
    profile = data.model_dump()
    profile['bmi'] = round(data.weight / (data.height / 100)**2, 2) if data.weight and data.height else None
    db.get(Profile, user.id).data = profile
    audit(db, user.id, 'profile.updated')
    db.commit()
    return profile

@app.get('/api/catalog/{kind}')
def catalog(kind: str, q: str = Query(default='', max_length=100), user=Depends(current_user), db=Depends(db_session)):
    if kind not in ('drugs','foods'):
        raise HTTPException(404)
    return search_catalog(db, Drug if kind == 'drugs' else Food, q)

@app.post('/api/check')
def check(data: Check, user=Depends(current_user), db=Depends(db_session)):
    drug, food = db.get(Drug, data.drug_id), db.get(Food, data.food_id)
    if not drug or not food:
        raise HTTPException(422, 'Selecione medicamento e alimento nas sugestões')
    profile = db.get(Profile, user.id).data if data.personalize else {}
    result = build_result(db, drug, food, profile)
    month = now()[:7]
    key = db.scalar(select(HistoryKey).where(HistoryKey.user_id == user.id, HistoryKey.month == month))
    if not key:
        key = HistoryKey(id=uid(), user_id=user.id, month=month)
        db.add(key)
        db.flush()
    record = History(id=uid(), owner_key=key.id, result=result)
    db.add(record)
    audit(db, user.id, 'interaction.checked')
    db.commit()
    return {**result, 'history_id':record.id, 'created_at':record.created_at}

def owned_history(db, user_id):
    return select(History).join(HistoryKey).where(HistoryKey.user_id == user_id).order_by(History.created_at.desc())

@app.get('/api/history')
def history(user=Depends(current_user), db=Depends(db_session)):
    return [{'id': h.id, 'created_at':h.created_at, 'result':h.result} for h in db.scalars(owned_history(db, user.id))]

@app.get('/api/privacy/export')
def export(user=Depends(current_user), db=Depends(db_session)):
    consent = db.get(Consent, user.id)
    records = [{'created_at':h.created_at, 'result':h.result} for h in db.scalars(owned_history(db, user.id))]
    logs = [{'action':a.action,'created_at':a.created_at} for a in db.scalars(select(Audit).where(Audit.actor == actor_hash(user.id)))]
    return {'user':public_user(user), 'profile':db.get(Profile,user.id).data, 'consent':{'version':consent.version, 'accepted_at':consent.accepted_at}, 'history':records, 'audit':logs, 'exported_at':now()}

def erase_user(db, user):
    keys = select(HistoryKey.id).where(HistoryKey.user_id == user.id)
    db.execute(delete(History).where(History.owner_key.in_(keys)))
    for model in (HistoryKey, Profile, Consent, Reset):
        db.execute(delete(model).where(model.user_id == user.id))
    db.execute(delete(Audit).where(Audit.actor == actor_hash(user.id)))
    db.delete(user)

@app.delete('/api/privacy/account')
def delete_account(data: PasswordRequest, response: Response, user=Depends(current_user), db=Depends(db_session)):
    if not password_matches(data.password, user.password):
        raise HTTPException(403, 'Senha incorreta')
    erase_user(db, user)
    db.commit()
    response.delete_cookie(COOKIE, path='/')
    return {'ok':True}

@app.get('/api/admin/overview')
def admin_overview(user=Depends(admin), db=Depends(db_session)):
    return {'datasets':[{'id':d.id,'version':d.version,'source':d.source,'count':d.count,'active':d.active,'created_at':d.created_at} for d in db.scalars(select(Dataset).order_by(Dataset.created_at.desc()))], 'users':[public_user(u) for u in db.scalars(select(User))], 'logs':[{'actor':a.actor[:12], 'action':a.action,'created_at':a.created_at} for a in db.scalars(select(Audit).order_by(Audit.created_at.desc()).limit(200))]}

@app.post('/api/admin/import')
def admin_import(data: ImportDataset, user=Depends(admin), db=Depends(db_session)):
    if db.scalar(select(Dataset).where(Dataset.version == data.version)):
        raise HTTPException(409, 'Versão já existente')
    dataset = import_dataset(db, data)
    audit(db, user.id, 'dataset.imported')
    db.commit()
    return {'version':dataset.version,'count':dataset.count}

@app.put('/api/admin/users/{user_id}')
def admin_update(user_id: str, data: AccountAction, user=Depends(admin), db=Depends(db_session)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404)
    if target.role == 'admin':
        raise HTTPException(409, 'Administradores são gerenciados pela linha de comando')
    target.active = data.active
    target.token_version += 1
    audit(db, user.id, 'account.status.changed')
    db.commit()
    return public_user(target)

@app.delete('/api/admin/users/{user_id}')
def admin_delete(user_id: str, data: PasswordRequest, user=Depends(admin), db=Depends(db_session)):
    if not password_matches(data.password, user.password):
        raise HTTPException(403, 'Senha incorreta')
    target = db.get(User, user_id)
    if not target or target.role == 'admin':
        raise HTTPException(409, 'Conta indisponível para exclusão')
    erase_user(db, target)
    audit(db, user.id, 'account.deleted')
    db.commit()
    return {'ok':True}

dist = Path(__file__).parent.parent / 'frontend' / 'dist'
if dist.exists():
    app.mount('/', StaticFiles(directory=dist, html=True), name='frontend')
