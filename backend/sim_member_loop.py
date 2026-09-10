# -*- coding: utf-8 -*-
"""第三阶段运行时模拟1：成员 待办→入口→提交→结果→收藏→历史。"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.models.saas import SysTenant, SysUser, SysTenantUser
from app.core.security import get_password_hash

e = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
S = sessionmaker(bind=e, autoflush=False, autocommit=False)
Base.metadata.create_all(e)


def ov():
    db = S()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = ov
db = S()
db.add(SysTenant(id=101, name='E'))
db.add(SysUser(id=2, phone='13800138000', password_hash=get_password_hash('123456')))
db.flush()
db.add(SysTenantUser(tenant_id=101, user_id=2, role='admin'))
db.commit()
db.close()

c = TestClient(app)
tok = c.post('/api/v1/auth/login', json={'phone': '13800138000', 'password': '123456'}).json()['data']['token']
H = {'Authorization': 'Bearer ' + tok, 'X-Tenant-ID': '101'}
ok = []


def check(name, cond, extra=''):
    ok.append(bool(cond))
    print(('PASS ' if cond else 'FAIL ') + name, extra)


r = c.post('/api/v1/admin/members', json={'phone': '13912345678'}, headers=H)
check('onboard', r.status_code == 200)
m = c.post('/api/v1/auth/login', json={'phone': '13912345678', 'password': '123456'}).json()['data']
mH = {'Authorization': 'Bearer ' + m['token'], 'X-Tenant-ID': '101'}
r = c.post('/api/v1/admin/resources', json={'content': '2+2=?', 'options': [{'key': 'A', 'text': '4'}],
                                             'correct_answer': ['A'], 'score': 10}, headers=H)
rid = r.json()['data']['id']
r = c.post('/api/v1/admin/tasks', json={'title': '数学小测', 'verification_mode': 'manual',
                                         'resource_ids': [rid]}, headers=H)
tid = r.json()['data']['task_id']
db = S()
from app.models.saas import Task as T
db.query(T).filter(T.id == tid).update({'status': 'published'})
db.commit()
db.close()

# 首页/待办
todo = c.get('/api/v1/member/member-tasks', headers=mH).json()['data']['items']
check('todo-visible', any(i['task_id'] == tid and i['status'] == 'pending' for i in todo))
# 作答入口（防泄漏）
entry = c.get(f'/api/v1/member/tasks/{tid}/entry', headers=mH)
check('entry-200', entry.status_code == 200)
qs = entry.json()['data']['questions']
check('entry-no-leak', qs and 'answer' not in qs[0] and 'correct_answer' not in qs[0], str(list(qs[0].keys())))
# 收藏
f = c.post('/api/v1/member/favorites', json={'resource_id': rid}, headers=mH)
check('fav-add', f.status_code in (200, 201), str(f.status_code))
fl = c.get('/api/v1/member/favorites', headers=mH).json()['data']['items']
check('fav-list-no-answer', len(fl) == 1 and 'answer' not in fl[0], str(list(fl[0].keys())))
# 提交
s = c.post('/api/v1/member/task-records/submit',
           json={'task_id': tid, 'time_spent': 45,
                 'answers': [{'resource_id': rid, 'answer': ['A']}]}, headers=mH)
check('submit', s.status_code == 200)
# 结果
recs = c.get('/api/v1/member/task-records', headers=mH).json()['data']['items']
check('history', len(recs) == 1 and recs[0]['task_title'] == '数学小测')
res = c.get(f"/api/v1/member/task-records/{recs[0]['record_id']}", headers=mH).json()['data']
check('result', res['status'] == 'submitted' and res['items'][0]['user_answer'] == ['A'], res['status'])
# 他人记录不可见
c.post('/api/v1/admin/members', json={'phone': '13900000002'}, headers=H)
m2 = c.post('/api/v1/auth/login', json={'phone': '13900000002', 'password': '123456'}).json()['data']
mH2 = {'Authorization': 'Bearer ' + m2['token'], 'X-Tenant-ID': '101'}
r2 = c.get(f"/api/v1/member/task-records/{recs[0]['record_id']}", headers=mH2)
check('result-owner-only', r2.status_code == 404)
print('ALL' if all(ok) else 'SOME FAILED', f'{sum(ok)}/{len(ok)}')
