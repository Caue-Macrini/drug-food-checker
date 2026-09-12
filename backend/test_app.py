import os, tempfile, hashlib, time
os.environ['DATABASE_URL'] = 'sqlite:///' + tempfile.mktemp(suffix='.db')
os.environ['JWT_SECRET'] = 'test-only-secret-' * 4
os.environ['SEED_DATA'] = 'true'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from main import app, hits, actor_hash
from models import Session, User, Reset, Profile, Consent, History, HistoryKey, Audit, Dataset
from services import adjusted_risk

@pytest.fixture
def client():
    hits.clear()
    with TestClient(app) as c:
        yield c

def signup(c, suffix='a'):
    import uuid
    email=f'{suffix}-{uuid.uuid4().hex[:8]}@example.com'
    response=c.post('/api/auth/register',json={'name':'Pessoa Teste','email':email,'password':'Senha-segura-123','consent':True})
    assert response.status_code==201,response.text
    return response.json(), email

def pair(c):
    d=c.get('/api/catalog/drugs?q=sinvastatina').json()[0]['id']
    f=c.get('/api/catalog/foods?q=toranja').json()[0]['id']
    return {'drug_id':d,'food_id':f}

def test_account_profile_query_history_export_delete(client):
    u,email=signup(client)
    assert client.get('/api/me').json()['email']==email
    r=client.put('/api/profile',json={'age':67,'weight':80,'height':180,'medications':['A','B','C'],'hepatic_insufficiency':True})
    assert r.json()['bmi']==24.69
    r=client.post('/api/check',json=pair(client))
    assert r.status_code==200,r.text
    result=r.json()
    assert result['found'] and result['risk'] is None
    assert result['evidence'][0]['modifiers']==[]
    assert client.get('/api/history').json()[0]['result']['drug']=='Sinvastatina'
    data=client.get('/api/privacy/export').json()
    assert data['consent']['version']=='1.0'
    assert 'password' not in data['user']
    assert client.request('DELETE','/api/privacy/account',json={'password':'wrong'}).status_code==403
    assert client.request('DELETE','/api/privacy/account',json={'password':'Senha-segura-123'}).status_code==200
    assert client.get('/api/me').status_code==401
    with Session() as db:
        assert db.get(User,u['id']) is None
        assert db.get(Profile,u['id']) is None
        assert db.get(Consent,u['id']) is None
        assert db.scalar(select(HistoryKey).where(HistoryKey.user_id==u['id'])) is None
        assert db.scalar(select(Audit).where(Audit.actor==actor_hash(u['id']))) is None

def test_consent_password_validation(client):
    body={'name':'Pessoa','email':'teste@example.com','password':'Senha-segura-123','consent':False}
    assert client.post('/api/auth/register',json=body).status_code==422
    body.update(consent=True,password='curta')
    assert client.post('/api/auth/register',json=body).status_code==422
    body['password']='🧪'*40
    assert client.post('/api/auth/register',json=body).status_code==422

def test_authorization_isolation_logout(client):
    assert client.get('/api/history').status_code==401
    u,email=signup(client)
    assert client.get('/api/admin/overview').status_code==403
    client.post('/api/check',json=pair(client))
    cookie=client.cookies.get('dfc_session')
    client.post('/api/auth/logout',json={})
    client.cookies.set('dfc_session',cookie)
    assert client.get('/api/me').status_code==401
    client.cookies.clear()
    signup(client,'b')
    assert client.get('/api/history').json()==[]

def test_unknown_pair_is_not_safe(client):
    signup(client)
    body=pair(client)
    body['food_id']=client.get('/api/catalog/foods?q=suco de laranja').json()[0]['id']
    result=client.post('/api/check',json=body).json()
    assert result['found'] is False and result['risk'] is None
    assert 'segurança' in result['notice']
    assert client.post('/api/check',json={'drug_id':'invalid','food_id':'invalid'}).status_code==422

@pytest.mark.parametrize('base,profile,flags,expected,count',[
 (0,{'hepatic_insufficiency':True},{'cyp450':True},1,1),
 (1,{'renal_stage':3},{'renal_excretion':True},2,1),
 (0,{'age':65,'medications':['a','b','c']},{},1,1),
 (0,{'age':65,'medications':['a','a','a']},{},0,0),
 (1,{'alcohol_frequency':4},{'hepatotoxic':True},2,1),
 (2,{'hepatic_insufficiency':True,'renal_stage':4},{'cyp450':True,'renal_excretion':True},2,2),
 (None,{'hepatic_insufficiency':True},{'cyp450':True},None,0),
 (0,{'age':64,'medications':['a','b','c'],'renal_stage':2},{'renal_excretion':True},0,0),
])
def test_rules(base,profile,flags,expected,count):
    level,reasons=adjusted_risk(base,profile,flags)
    assert level==expected and len(reasons)==count

def test_reset_single_use_revokes_sessions(client):
    u,email=signup(client)
    with Session() as db:
        db.add(Reset(token_hash=hashlib.sha256(b'token-de-teste-muito-longo').hexdigest(),user_id=u['id'],expires=int(time.time())+100))
        db.commit()
    data={'token':'token-de-teste-muito-longo','password':'Nova-senha-12345'}
    assert client.post('/api/auth/reset',json=data).status_code==200
    assert client.get('/api/me').status_code==401
    assert client.post('/api/auth/reset',json=data).status_code==400
    assert client.post('/api/auth/login',json={'email':email,'password':'Senha-segura-123'}).status_code==401
    assert client.post('/api/auth/login',json={'email':email,'password':'Nova-senha-12345'}).status_code==200

def test_csrf_and_rate_limit(client):
    signup(client)
    assert client.put('/api/profile',json={},headers={'Origin':'https://evil.example'}).status_code==403
    assert client.put('/api/profile',content='{}',headers={'Content-Type':'text/plain'}).status_code==415
    for _ in range(121):
        last=client.get('/api/health')
    assert last.status_code==429

def test_admin_import_version_snapshot_and_management(client):
    u,_=signup(client,'admin')
    with Session() as db:
        db.get(User,u['id']).role='admin'
        db.commit()
    old=client.post('/api/check',json=pair(client)).json()
    from pathlib import Path
    import json
    data=json.loads((Path(__file__).parent.parent/'data/starter.json').read_text(encoding='utf-8'))
    data['version']='test-reviewed'
    data['rows'][0].update(reviewed=True,base_risk=1,risk_basis='Fictício: exclusivamente teste automatizado')
    assert client.post('/api/admin/import',json=data).status_code==200
    assert client.post('/api/admin/import',json=data).status_code==409
    new=client.post('/api/check',json=pair(client)).json()
    assert new['risk']==1
    historical=client.get('/api/history').json()
    assert next(h for h in historical if h['id']==old['history_id'])['result']['risk'] is None
    assert len([d for d in client.get('/api/admin/overview').json()['datasets'] if d['active']])==1
    assert client.put('/api/admin/users/'+u['id'],json={'active':False}).status_code==409
    data['version']='test-unreviewed'
    data['rows'][0]['reviewed']=False
    assert client.post('/api/admin/import',json=data).status_code==200
    assert client.post('/api/check',json=pair(client)).json()['risk'] is None
