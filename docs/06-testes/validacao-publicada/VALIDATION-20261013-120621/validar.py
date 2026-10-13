#!/usr/bin/env python3
"""Validação real e sequencial. Cria dados; nunca limpa, implanta ou altera a aplicação.

Execução: python3 validar.py --private-dir /diretorio/restrito/novo
Usa apenas a biblioteca padrão; requer Docker local e acesso autorizado à homologação.
Uma nova execução recebe outro identificador e novas credenciais (modo 600).
"""
import argparse
import concurrent.futures
import csv
import hashlib
import http.cookiejar
import io
import json
import os
import re
import secrets
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[4]
BASE = 'https://projeto-integrador.tesseratointegra.com.br'
TZ = ZoneInfo('America/Sao_Paulo')
COMPOSE = ['docker', 'compose', '-p', 'codigo-do-futuro', '--env-file', str(ROOT/'deploy/production.env'), '-f', str(ROOT/'compose.production.yaml')]
LIMIT = 650
REQUESTS = []
CASES = []
CLIENTS = {}

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()

def class_code(alias):
    suffix={'queue':'Q','race':'R','academic':'A','other':'O','manual':'M','no-waitlist':'N','expired':'X','invalid':'I','started':'S','bypass':'B'}[alias.lower()]
    return RUN+'-'+suffix

def safe_endpoint(path):
    if path.startswith('/senha/redefinir/') and len(path.removeprefix('/senha/redefinir/').strip('/').split('/'))>=2:
        return '/senha/redefinir/<uid>/<token>/'
    return path

def orm(code):
    # Code travels through stdin, never through command line arguments or logs.
    header = 'import django,json,hashlib\nfrom django.core.serializers.json import DjangoJSONEncoder\ndjango.setup()\nfrom django.apps import apps\nfrom django.db import connection\n'
    r = subprocess.run(COMPOSE+['exec','-T','app','python','-'], input=header+code, text=True, capture_output=True, timeout=30)
    if r.returncode:
        raise RuntimeError('Consulta/preparação Django falhou; saída omitida para proteger dados')
    return json.loads(r.stdout)

SCOPES = {
    'accounts.User':'full_name__startswith', 'people.Participant':'full_name__startswith',
    'people.Guardian':'full_name__startswith', 'people.Instructor':'user__full_name__startswith',
    'people.Institution':'name__startswith', 'people.ParticipantGuardian':'participant__full_name__startswith',
    'workshops.Workshop':'title__startswith', 'workshops.ClassGroup':'code__startswith',
    'workshops.ClassInstructor':'class_group__code__startswith','workshops.Meeting':'class_group__code__startswith',
    'enrollments.Enrollment':'class_group__code__startswith','enrollments.EnrollmentStatusHistory':'enrollment__class_group__code__startswith',
    'learning.Attendance':'enrollment__class_group__code__startswith','learning.StudentProject':'enrollment__class_group__code__startswith',
    'learning.Evaluation':'enrollment__class_group__code__startswith','learning.Certificate':'enrollment__class_group__code__startswith',
}
EXCLUDE = {'password','email','contact_email','contact_phone','phone','cpf','document','birth_date'}

def snapshot():
    return orm('''
with connection.cursor() as c: c.execute('SET default_transaction_read_only = on')
run = %r
scopes = %r
exclude = %r
out = {}
for label,lookup in scopes.items():
 m=apps.get_model(label)
 fields=[f.attname for f in m._meta.fields if f.name not in exclude]
 out[label]=list(m.objects.filter(**{lookup:run}).order_by('pk').values(*fields))
print(json.dumps(out,cls=DjangoJSONEncoder))
''' % (RUN, SCOPES, EXCLUDE))

def existing_hash():
    return orm('''
with connection.cursor() as c: c.execute('SET default_transaction_read_only = on')
out={}
for label,lookup in %r.items():
 m=apps.get_model(label)
 rows=list(m.objects.exclude(**{lookup:%r}).order_by('pk').values())
 out[label]={'rows':len(rows),'sha256':hashlib.sha256(json.dumps(rows,cls=DjangoJSONEncoder,sort_keys=True).encode()).hexdigest()}
print(json.dumps(out))
''' % (SCOPES,RUN))

def rows(s,table):
    return s[table]

def find(s,table,**filters):
    matches=[r for r in rows(s,table) if all(str(r.get(k))==str(v) for k,v in filters.items())]
    if len(matches)!=1:
        raise RuntimeError('Pré-condição ausente ou ambígua: '+table)
    return matches[0]

def changes(before,after):
    out={}
    for table in before:
        b={str(r['id']):r for r in before[table]};a={str(r['id']):r for r in after[table]}
        diff=[{'id':pk,'before':b.get(pk),'after':a.get(pk)} for pk in b.keys()|a.keys() if b.get(pk)!=a.get(pk)]
        if diff: out[table]=diff
    return out

class Forms(HTMLParser):
    def __init__(self,text):
        super().__init__();self.forms=[];self.form=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form':
            self.form={'action':a.get('action',''),'method':a.get('method','get').upper(),'fields':{},'names':set()};self.forms.append(self.form)
        elif self.form is not None and tag in ('input','select','textarea','button') and 'name' in a:
            self.form['names'].add(a['name'])
            if tag=='input' and 'disabled' not in a:
                if a.get('type') not in ('checkbox','radio') or 'checked' in a:
                    self.form['fields'][a['name']]=a.get('value','')
    def handle_endtag(self,tag):
        if tag=='form': self.form=None

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw): return None

class Session:
    def __init__(self,role):
        self.role=role;self.jar=http.cookiejar.CookieJar()
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar),NoRedirect())
    def request(self,path,method='GET',data=None):
        if len(REQUESTS)>=LIMIT: raise RuntimeError('Limite de requisições atingido')
        url=urllib.parse.urljoin(BASE,path)
        assert urllib.parse.urlparse(url).hostname==urllib.parse.urlparse(BASE).hostname
        headers={'User-Agent':'CodigoDoFuturo-FunctionalValidation/'+RUN}
        payload=None
        if data is not None:
            payload=urllib.parse.urlencode(data).encode();headers.update({'Referer':BASE+path.split('?')[0],'Origin':BASE,'Content-Type':'application/x-www-form-urlencoded'})
        start=time.monotonic()
        try:r=self.opener.open(urllib.request.Request(url,data=payload,headers=headers,method=method),timeout=20)
        except urllib.error.HTTPError as e:r=e
        body=r.read();text=body.decode('utf-8',errors='replace')
        location=r.headers.get('Location','')
        if '/senha/redefinir/' in location: location='/senha/redefinir/<uid>/<token>/'
        record={'timestamp':datetime.now(TZ).isoformat(),'profile':self.role,'method':method,'endpoint':safe_endpoint(path),'status':r.status,'content_type':r.headers.get('Content-Type',''),'location':location,'bytes':len(body),'elapsed_ms':round((time.monotonic()-start)*1000)}
        REQUESTS.append(record)
        r.close();time.sleep(.05)
        return {'status':record['status'],'text':text,'body':body,'headers':dict(r.headers),'request':record}
    def post(self,path,data,source=None,csrf='valid',verify=True):
        page=self.request(source or path)
        forms=Forms(page['text']).forms
        matches=[f for f in forms if f['method']=='POST' and urllib.parse.urljoin(BASE+(source or path),f['action'])==BASE+path]
        if verify and not matches: raise RuntimeError('Formulário POST não encontrado no HTML servido: '+path)
        chosen=matches[0] if matches else next((f for f in forms if 'csrfmiddlewaretoken' in f['fields']),None)
        if chosen is None: raise RuntimeError('CSRF não encontrado em formulário servido')
        payload=dict(data)
        if csrf=='valid':payload['csrfmiddlewaretoken']=chosen['fields']['csrfmiddlewaretoken']
        elif csrf=='invalid':payload['csrfmiddlewaretoken']='x'*64
        return self.request(path,'POST',payload)

def test(name,group,client,path,method='GET',data=None,source=None,expected='',checks=None,unchanged=False,csrf='valid',verify=True):
    before=snapshot();first=len(REQUESTS);observed={};r=None
    try:
        r=client.post(path,data or {},source,csrf,verify) if method=='POST' else client.request(path,method)
        after=snapshot()
        for label,fn in (checks or {}).items():
            try:observed[label]=bool(fn(r,before,after))
            except Exception:observed[label]=False
        if unchanged:observed['dados_de_negocio_preservados']=before==after
        classification='APROVADO' if observed and all(observed.values()) else 'REPROVADO'
        detail='Todas as verificações passaram' if classification=='APROVADO' else 'Falharam: '+', '.join(k for k,v in observed.items() if not v)
    except Exception as e:
        after=snapshot();classification='BLOQUEADO';detail='Erro do executor ou pré-condição: '+type(e).__name__
    record={'id':f'HTTP-{len(CASES)+1:03d}','functionality':name,'group':group,'endpoint':safe_endpoint(path),'method':method,'profile':client.role,'preconditions':{'run':RUN,'state_sha256':digest(before)},'expected':expected,'observed':detail,'status':r['status'] if r else None,'checks':observed,'classification':classification,'timestamp':datetime.now(TZ).isoformat(),'requests':list(range(first+1,len(REQUESTS)+1)),'persisted_effects':changes(before,after),'state_after_sha256':digest(after)}
    CASES.append(record);save()
    print(record['id'],classification,name,flush=True)
    return r,after

def save():
    (OUT/'matriz.json').write_text(json.dumps(CASES,indent=2,ensure_ascii=False))
    (OUT/'requisicoes.json').write_text(json.dumps(REQUESTS,indent=2,ensure_ascii=False))

def status(n):return {'http_esperado':lambda r,b,a:r['status']==n}
def get(name,group,c,path,n=200,extra=None):
    return test(name,group,c,path,expected=f'HTTP {n}; conteúdo e isolamento conferidos quando aplicável',checks=status(n)|(extra or {}),unchanged=True)
def post(name,group,c,path,data=None,source=None,n=302,check=None,unchanged=False,expected=None,**kw):
    return test(name,group,c,path,'POST',data,source,expected or f'HTTP {n}; regra e efeito persistido correspondentes',status(n)|(check or {}),unchanged,**kw)

def prep():
    old=existing_hash();(OUT/'dados-existentes-inicial-hashes.json').write_text(json.dumps(old,indent=2))
    # No public unauthenticated endpoint can provision the first isolated administrator.
    # Only that account is bootstrapped. Other accounts and every business entity use HTTP.
    creds={alias:{'email':f'{RUN.lower()}-{alias}@validation.codigodofuturo.local','password':secrets.token_urlsafe(30)} for alias in ['admin','i1','i2','p1','p2','p3','minor']}
    fd=os.open(PRIVATE/'credentials.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w') as f:json.dump(creds,f)
    admin=creds['admin']
    orm('''
from apps.accounts.models import User
assert not User.objects.filter(full_name__startswith=%r).exists()
u=User.objects.create_superuser(email=%r,password=%r,full_name=%r,role='ADMIN')
print(json.dumps({'created':True}))
''' % (RUN,admin['email'],admin['password'],RUN+' ADMIN'))
    return creds

def login(alias,creds):
    c=Session({'admin':'ADMIN','i1':'INSTRUCTOR_1','i2':'INSTRUCTOR_2','p1':'PARTICIPANT_1','p2':'PARTICIPANT_2','p3':'PARTICIPANT_3','minor':'PARTICIPANT_MINOR'}[alias]);CLIENTS[alias]=c
    post('Login correto '+c.role,'Autenticação',c,'/entrar/',{'username':creds[alias]['email'],'password':creds[alias]['password']},check={'sessao_iniciada':lambda r,b,a:any(x.name=='sessionid' for x in c.jar),'redirect_home':lambda r,b,a:r['headers'].get('Location')=='/'})
    return c

def main():
    creds=prep();anon=Session('ANONYMOUS');CLIENTS['anon']=anon
    get('Health por HTTPS','Disponibilidade',anon,'/healthz/',extra={'servico_ok':lambda r,b,a:json.loads(r['text'])=={'status':'ok','service':'codigo-do-futuro'}})
    get('Ready com banco','Disponibilidade',anon,'/readyz/',extra={'banco_ready':lambda r,b,a:json.loads(r['text'])['status']=='ready'})
    page,_=get('Login público HTTPS','Disponibilidade',anon,'/entrar/')
    assets=set(re.findall(r'(?:href|src)="([^"]*/static/[^"]+)"',page['text']))
    for asset in assets:get('Estático do login','Disponibilidade',anon,asset,extra={'conteudo_nao_vazio':lambda r,b,a:len(r['body'])>100,'css':lambda r,b,a:'text/css' in r['headers'].get('Content-Type','')})
    get('HTTP redireciona para HTTPS','Disponibilidade',anon,BASE.replace('https:','http:')+'/entrar/',301,{'destino_https':lambda r,b,a:r['headers'].get('Location')==BASE+'/entrar/'})
    for path in ['/','/pessoas/','/oficinas/','/inscricoes/','/acompanhamento/frequencia/','/acompanhamento/certificados/','/painel/']:
        get('Anônimo em página protegida','Autorização',anon,path,302,{'destino_login':lambda r,b,a:r['headers'].get('Location','').startswith('/entrar/?next=')})
    post('Login incorreto','Autenticação',anon,'/entrar/',{'username':creds['p1']['email'],'password':secrets.token_urlsafe(24)},n=200,unchanged=True,check={'erro_visivel':lambda r,b,a:'E-mail ou senha inválidos' in r['text'],'sem_sessao':lambda r,b,a:not any(x.name=='sessionid' for x in anon.jar)})
    admin=login('admin',creds)
    # UserAdmin is an actual served provisioning endpoint; all remaining accounts use it.
    for alias in ['i1','i2','p1','p2','p3','minor']:
        role='INSTRUCTOR' if alias.startswith('i') else 'PARTICIPANT'
        data={'email':creds[alias]['email'],'full_name':RUN+' '+alias.upper(),'role':role,'password1':creds[alias]['password'],'password2':creds[alias]['password'],'_save':'Salvar'}
        post('Provisionar conta '+alias,'Preparação HTTP',admin,'/admin/accounts/user/add/',data,check={'usuario_novo_perfil':lambda r,b,a,alias=alias,role=role:any(x['full_name']==RUN+' '+alias.upper() and x['role']==role for x in a['accounts.User'])})
    for alias in ['i1','i2','p1','p2','p3','minor']:login(alias,creds)
    for alias in ['admin','i1','p1']:
        c=CLIENTS[alias]
        get('Flags cookies '+c.role,'Autenticação',c,'/',extra={'cookies_seguros_httponly_samesite':lambda r,b,a,c=c:all(x.secure and 'HttpOnly' in x._rest and x._rest.get('SameSite')=='Lax' for x in c.jar if x.name in {'sessionid','csrftoken'})})
    for alias in ['i1','p1']:
        for path in ['/pessoas/','/pessoas/participantes/','/oficinas/nova/','/oficinas/turmas/nova/','/admin/accounts/user/add/']:
            n=302 if path.startswith('/admin/') else 403
            get('Perfil insuficiente '+alias,'Autorização',CLIENTS[alias],path,n)
    post('POST sem CSRF','Autorização',admin,'/pessoas/participantes/novo/',{},n=403,unchanged=True,csrf='missing')
    post('POST CSRF inválido','Autorização',admin,'/pessoas/participantes/novo/',{},n=403,unchanged=True,csrf='invalid')
    test('Método DELETE inadequado','Autorização',admin,'/pessoas/participantes/novo/','DELETE',expected='CSRF rejeita método inseguro sem token; nenhum dado criado',checks=status(403),unchanged=True)
    get('Identificador inexistente','Autorização',admin,'/pessoas/participantes/'+str(uuid.uuid4())+'/',404)
    people(admin)
    workshops(admin)
    enrollments(admin)
    academic(admin)
    reports(admin)
    recovery(creds)
    c=CLIENTS['p3']
    get('Logout por GET rejeitado','Autenticação',c,'/sair/',405)
    post('Logout por POST','Autenticação',c,'/sair/',source='/',unchanged=True,check={'redirect_login':lambda r,b,a:r['headers'].get('Location')=='/entrar/'})
    get('Acesso após logout','Autenticação',c,'/',302,{'redirect_login':lambda r,b,a:r['headers'].get('Location','').startswith('/entrar/?next=')})

def people(admin):
    now=datetime.now(TZ);s=snapshot();users={alias:find(s,'accounts.User',full_name=RUN+' '+alias.upper())['id'] for alias in ['i1','i2','p1','p2','p3','minor']}
    post('Participante campos obrigatórios','Pessoas',admin,'/pessoas/participantes/novo/',{},n=200,unchanged=True,check={'erros_formulario':lambda r,b,a:'Este campo é obrigatório' in r['text']})
    invalid={'full_name':RUN+' INVALID','birth_date':'bad-date','cpf':'11111111111','contact_email':'invalid-email','phone':'123','is_active':'on'}
    post('Formatos de participante inválidos','Pessoas',admin,'/pessoas/participantes/novo/',invalid,n=200,unchanged=True,check={'campos_rejeitados':lambda r,b,a:r['text'].count('field-error')>=3})
    # A mathematically valid synthetic CPF is generated to avoid using existing examples.
    prefix=[secrets.randbelow(10) for _ in range(9)]
    for size in [9,10]:
        total=sum(v*w for v,w in zip(prefix,range(size+1,1,-1)));d=11-total%11;prefix.append(0 if d>=10 else d)
    fake_cpf=''.join(map(str,prefix));SYNTHETIC['cpf']=fake_cpf
    for alias in ['p1','p2','p3','minor']:
        data={'user':users[alias],'full_name':RUN+' '+alias.upper(),'birth_date':f'{now.year-(16 if alias=="minor" else 19)}-01-01','is_active':'on','privacy_consent_at':now.strftime('%Y-%m-%dT%H:%M')}
        if alias=='p1':data['cpf']=fake_cpf
        post('Criar participante '+alias,'Pessoas',admin,'/pessoas/participantes/novo/',data,check={'perfil_vinculado':lambda r,b,a,alias=alias:find(a,'people.Participant',user_id=users[alias])['full_name']==RUN+' '+alias.upper()})
        PEOPLE_DATA[alias]=data
    s=snapshot();PARTICIPANTS.update({alias:find(s,'people.Participant',user_id=users[alias])['id'] for alias in PEOPLE_DATA})
    get('Pesquisar participante e CPF mascarado','Pessoas',admin,'/pessoas/participantes/?q='+RUN,extra={'registros_da_execucao':lambda r,b,a:RUN+' P1' in r['text'],'cpf_integral_ausente':lambda r,b,a:fake_cpf not in r['text'] and (fake_cpf[:3]+'.'+fake_cpf[3:6]+'.'+fake_cpf[6:9]+'-'+fake_cpf[9:]) not in r['text'],'cpf_mascarado':lambda r,b,a:('***.'+fake_cpf[3:6]+'.'+fake_cpf[6:9]+'-**') in r['text']})
    get('Consultar participante','Pessoas',admin,f'/pessoas/participantes/{PARTICIPANTS["p1"]}/')
    edited=PEOPLE_DATA['p1']|{'image_authorization':'on'}
    post('Editar participante','Pessoas',admin,f'/pessoas/participantes/{PARTICIPANTS["p1"]}/editar/',edited,check={'autorizacao_persistida':lambda r,b,a:find(a,'people.Participant',id=PARTICIPANTS['p1'])['image_authorization'] is True})
    duplicate=PEOPLE_DATA['p1']|{'user':'','full_name':RUN+' DUPLICATE'}
    post('CPF duplicado','Pessoas',admin,'/pessoas/participantes/novo/',duplicate,n=200,unchanged=True,check={'duplicidade_visivel':lambda r,b,a:'já existe' in r['text']})
    post('Responsável telefone inválido','Pessoas',admin,'/pessoas/responsaveis/novo/',{'full_name':RUN+' GUARDIAN_INVALID','phone':'123'},n=200,unchanged=True,check={'erro_formulario':lambda r,b,a:'field-error' in r['text']})
    data={'full_name':RUN+' GUARDIAN','phone':'16999990000','is_active':'on'}
    post('Criar responsável fictício','Pessoas',admin,'/pessoas/responsaveis/novo/',data,check={'responsavel_criado':lambda r,b,a:len(a['people.Guardian'])==len(b['people.Guardian'])+1})
    s=snapshot();guardian=find(s,'people.Guardian',full_name=RUN+' GUARDIAN')['id'];GLOBALS['guardian']=guardian
    get('Pesquisar responsável','Pessoas',admin,'/pessoas/responsaveis/?q='+RUN,extra={'encontrado':lambda r,b,a:RUN+' GUARDIAN' in r['text']})
    post('Editar responsável','Pessoas',admin,f'/pessoas/responsaveis/{guardian}/editar/',data|{'full_name':RUN+' GUARDIAN_EDITED'},check={'nome_editado':lambda r,b,a:find(a,'people.Guardian',id=guardian)['full_name'].endswith('EDITED')})
    # Guardian is linked only after the minor enrollment negative case.
    for alias in ['i1','i2']:
        data={'user':users[alias],'biography':RUN+' biografia fictícia','specialties':'Python','is_active':'on'}
        post('Criar perfil instrutor '+alias,'Pessoas',admin,'/pessoas/instrutores/novo/',data,check={'perfil_instrutor':lambda r,b,a,alias=alias:find(a,'people.Instructor',user_id=users[alias])['is_active']})
    s=snapshot();INSTRUCTORS.update({alias:find(s,'people.Instructor',user_id=users[alias])['id'] for alias in ['i1','i2']})
    get('Pesquisar instrutor','Pessoas',admin,'/pessoas/instrutores/?q='+RUN,extra={'instrutores_encontrados':lambda r,b,a:RUN+' I1' in r['text'] and RUN+' I2' in r['text']})
    post('Criar instituição','Pessoas',admin,'/pessoas/instituicoes/nova/',{'name':RUN+' INSTITUTION','address':RUN+' endereço fictício','is_active':'on'},check={'instituicao_criada':lambda r,b,a:len(a['people.Institution'])==1})
    institution=find(snapshot(),'people.Institution',name=RUN+' INSTITUTION')['id'];GLOBALS['institution']=institution
    get('Pesquisar instituição','Pessoas',admin,'/pessoas/instituicoes/?q='+RUN,extra={'instituicao_encontrada':lambda r,b,a:RUN+' INSTITUTION' in r['text']})
    post('Editar instituição','Pessoas',admin,f'/pessoas/instituicoes/{institution}/editar/',{'name':RUN+' INSTITUTION','address':RUN+' endereço fictício editado','is_active':'on'},check={'endereco_editado':lambda r,b,a:find(a,'people.Institution',id=institution)['address'].endswith('editado')})
    for alias in ['p1','i1']:
        get('Dados pessoais protegidos '+alias,'Autorização',CLIENTS[alias],f'/pessoas/participantes/{PARTICIPANTS["p2"]}/',403)

def workshops(admin):
    today=datetime.now(TZ).date();GLOBALS['today']=today
    if not snapshot()['workshops.Workshop']:
        data={'title':RUN+' WORKSHOP','slug':RUN.lower(),'summary':RUN+' resumo','objective':RUN+' objetivo','syllabus':RUN+' conteúdo','estimated_hours':'4.00'}
        post('Criar oficina rascunho','Oficinas',admin,'/oficinas/nova/',data,check={'rascunho':lambda r,b,a:find(a,'workshops.Workshop',slug=RUN.lower())['status']=='DRAFT'})
        w=find(snapshot(),'workshops.Workshop',slug=RUN.lower())['id'];GLOBALS['workshop']=w
        post('Oficina slug duplicado','Oficinas',admin,'/oficinas/nova/',data,n=200,unchanged=True,check={'erro_duplicidade':lambda r,b,a:'já existe' in r['text']})
        post('Editar oficina','Oficinas',admin,f'/oficinas/{w}/editar/',data|{'summary':RUN+' resumo editado'},check={'resumo_editado':lambda r,b,a:find(a,'workshops.Workshop',id=w)['summary'].endswith('editado')})
        post('Publicar oficina','Oficinas',admin,f'/oficinas/{w}/situacao/published/',source=f'/oficinas/{w}/',check={'publicada':lambda r,b,a:find(a,'workshops.Workshop',id=w)['status']=='PUBLISHED'})
        get('Pesquisar oficina','Oficinas',admin,'/oficinas/?q='+RUN,extra={'encontrada':lambda r,b,a:RUN+' WORKSHOP' in r['text']})
    w=find(snapshot(),'workshops.Workshop',slug=RUN.lower())['id'];GLOBALS['workshop']=w
    base={'workshop':w,'institution':GLOBALS['institution'],'location':RUN+' sala fictícia','registration_opens_at':(today-timedelta(days=1)).isoformat()+'T00:00','registration_closes_at':today.isoformat()+'T23:00','end_date':(today+timedelta(days=7)).isoformat(),'waitlist_enabled':'on'}
    bad=base|{'code':RUN+'-INVALID','title':RUN+' INVALID','capacity':'0','start_date':(today+timedelta(days=9)).isoformat()}
    post('Turma datas e capacidade inválidas','Turmas',admin,'/oficinas/turmas/nova/',bad,n=200,unchanged=True,check={'erros_formulario':lambda r,b,a:'field-error' in r['text']})
    for alias,capacity,offset in [('queue',1,1),('race',1,1),('academic',4,0),('other',1,1)]:
        data=base|{'code':class_code(alias),'title':RUN+' '+alias.upper(),'capacity':str(capacity),'start_date':(today+timedelta(days=offset)).isoformat()}
        CLASS_DATA[alias]=data
        post('Criar turma '+alias,'Turmas',admin,'/oficinas/turmas/nova/',data,check={'turma_planejada':lambda r,b,a,alias=alias:find(a,'workshops.ClassGroup',code=class_code(alias))['status']=='PLANNED'})
        CLASSES[alias]=find(snapshot(),'workshops.ClassGroup',code=class_code(alias))['id']
        cid=CLASSES[alias]
        if alias=='queue':
            post('Abrir sem instrutor bloqueado','Turmas',admin,f'/oficinas/turmas/{cid}/situacao/open/',source=f'/oficinas/turmas/{cid}/',unchanged=True,check={'planejada_preservada':lambda r,b,a:find(a,'workshops.ClassGroup',id=cid)['status']=='PLANNED'})
            post('Editar turma planejada','Turmas',admin,f'/oficinas/turmas/{cid}/editar/',data|{'location':RUN+' sala editada'},check={'local_editado':lambda r,b,a:find(a,'workshops.ClassGroup',id=cid)['location'].endswith('editada')})
        instructor=INSTRUCTORS['i2' if alias=='other' else 'i1']
        post('Vincular instrutor '+alias,'Turmas',admin,f'/oficinas/turmas/{cid}/instrutores/vincular/',{'instructor':instructor,'is_lead':'on'},check={'vinculo_persistido':lambda r,b,a,cid=cid:find(a,'workshops.ClassInstructor',class_group_id=cid)['is_lead']})
        post('Abrir inscrições '+alias,'Turmas',admin,f'/oficinas/turmas/{cid}/situacao/open/',source=f'/oficinas/turmas/{cid}/',check={'turma_aberta':lambda r,b,a,cid=cid:find(a,'workshops.ClassGroup',id=cid)['status']=='OPEN'})
    cid=CLASSES['academic']
    post('Iniciar sem encontros bloqueado','Turmas',admin,f'/oficinas/turmas/{cid}/situacao/in_progress/',source=f'/oficinas/turmas/{cid}/',unchanged=True,check={'permanece_aberta':lambda r,b,a:find(a,'workshops.ClassGroup',id=cid)['status']=='OPEN'})
    path=f'/oficinas/turmas/{cid}/encontros/novo/'
    invalid={'title':RUN+' BAD_MEETING','starts_at':(today-timedelta(days=2)).isoformat()+'T01:00','ends_at':(today-timedelta(days=2)).isoformat()+'T00:00'}
    post('Encontro fora período e fim inválido','Encontros',admin,path,invalid,n=200,unchanged=True,check={'erro_formulario':lambda r,b,a:'field-error' in r['text']})
    for i in range(4):
        data={'title':RUN+f' MEETING_{i+1}','description':RUN,'starts_at':today.isoformat()+f'T0{i}:00','ends_at':today.isoformat()+f'T0{i+1}:00'}
        post('Criar encontro '+str(i+1),'Encontros',admin,path,data,check={'encontro_criado':lambda r,b,a:len(a['workshops.Meeting'])==len(b['workshops.Meeting'])+1})
        MEETINGS.append(find(snapshot(),'workshops.Meeting',title=data['title'])['id'])
    post('Encontro início duplicado','Encontros',admin,path,{'title':RUN+' DUP_MEETING','starts_at':today.isoformat()+'T00:00','ends_at':today.isoformat()+'T01:00'},n=200,unchanged=True,check={'erro_duplicidade':lambda r,b,a:'já existe' in r['text']})
    mid=MEETINGS[0]
    post('Editar encontro planejado','Encontros',admin,f'/oficinas/encontros/{mid}/editar/',{'title':RUN+' MEETING_1','description':RUN+' editado','starts_at':today.isoformat()+'T00:00','ends_at':today.isoformat()+'T01:00'},check={'descricao_editada':lambda r,b,a:find(a,'workshops.Meeting',id=mid)['description'].endswith('editado')})
    data={'title':RUN+' FUTURE_MEETING','starts_at':(today+timedelta(days=1)).isoformat()+'T08:00','ends_at':(today+timedelta(days=1)).isoformat()+'T09:00'}
    post('Criar encontro futuro','Encontros',admin,path,data,check={'futuro_planejado':lambda r,b,a:find(a,'workshops.Meeting',title=data['title'])['status']=='PLANNED'})
    GLOBALS['future']=find(snapshot(),'workshops.Meeting',title=data['title'])['id']
    for alias in ['i1','i2']:
        own=CLASSES['academic' if alias=='i1' else 'other'];other=CLASSES['other' if alias=='i1' else 'academic']
        get('Instrutor lista somente próprias turmas '+alias,'Autorização',CLIENTS[alias],'/oficinas/turmas/?q='+RUN,extra={'propria_visivel':lambda r,b,a,own=own:own in r['text'],'terceira_oculta':lambda r,b,a,other=other:other not in r['text']})
        get('Instrutor turma alheia '+alias,'Autorização',CLIENTS[alias],f'/oficinas/turmas/{other}/',404)
    get('Editar turma aberta bloqueado','Turmas',admin,f'/oficinas/turmas/{cid}/editar/',403)
    get('Vincular instrutor após abertura bloqueado','Turmas',admin,f'/oficinas/turmas/{cid}/instrutores/vincular/',403)

def request_enrollment(alias,cls,admin=False):
    cid=CLASSES[cls];c=CLIENTS['admin' if admin else alias]
    if admin:
        path='/inscricoes/nova/';data={'participant':PARTICIPANTS[alias],'class_group':cid};source=None
    else:
        path=f'/inscricoes/turmas/{cid}/solicitar/';data={};source='/inscricoes/turmas-disponiveis/'
    post('Solicitar inscrição '+alias+' '+cls,'Inscrições',c,path,data,source,check={'inscricao_nova':lambda r,b,a:len(a['enrollments.Enrollment'])==len(b['enrollments.Enrollment'])+1})
    e=find(snapshot(),'enrollments.Enrollment',participant_id=PARTICIPANTS[alias],class_group_id=cid);ENROLLMENTS[(alias,cls)]=e['id'];return e['id']

def enrollments(admin):
    cid=CLASSES['queue'];path=f'/inscricoes/turmas/{cid}/solicitar/'
    post('Menor sem responsável bloqueado','Inscrições',CLIENTS['minor'],path,source='/inscricoes/turmas-disponiveis/',unchanged=True,check={'nenhuma_inscricao':lambda r,b,a:len(a['enrollments.Enrollment'])==0})
    post('Vincular responsável ao menor','Pessoas',admin,f'/pessoas/participantes/{PARTICIPANTS["minor"]}/responsaveis/vincular/',{'guardian':GLOBALS['guardian'],'relationship':'LEGAL_GUARDIAN','is_primary':'on'},check={'vinculo_principal':lambda r,b,a:find(a,'people.ParticipantGuardian',participant_id=PARTICIPANTS['minor'])['is_primary']})
    post('Responsável duplicado bloqueado','Pessoas',admin,f'/pessoas/participantes/{PARTICIPANTS["minor"]}/responsaveis/vincular/',{'guardian':GLOBALS['guardian'],'relationship':'OTHER','is_primary':'on'},n=200,unchanged=True,check={'erros_visiveis':lambda r,b,a:'field-error' in r['text']})
    e1=request_enrollment('p1','queue');request_enrollment('minor','queue')
    post('Inscrição duplicada bloqueada','Inscrições',CLIENTS['p1'],path,source='/',verify=False,unchanged=True,check={'uma_por_participante_turma':lambda r,b,a:len([e for e in a['enrollments.Enrollment'] if e['participant_id']==PARTICIPANTS['p1'] and e['class_group_id']==cid])==1})
    get('Contadores sem ocupar vaga pendente','Vagas',admin,f'/inscricoes/turmas/{cid}/fila/',extra={'zero_confirmadas':lambda r,b,a:'Confirmadas</small><strong>0' in r['text'],'uma_vaga':lambda r,b,a:'Disponíveis</small><strong>1' in r['text']})
    post('Confirmar inscrição e ocupar vaga','Vagas',admin,f'/inscricoes/{e1}/confirmar/',{},check={'confirmada':lambda r,b,a:find(a,'enrollments.Enrollment',id=e1)['status']=='CONFIRMED'})
    get('Contadores turma lotada','Vagas',admin,f'/inscricoes/turmas/{cid}/fila/',extra={'uma_confirmada':lambda r,b,a:'Confirmadas</small><strong>1' in r['text'],'zero_vagas':lambda r,b,a:'Disponíveis</small><strong>0' in r['text']})
    e2=request_enrollment('p2','queue');e3=request_enrollment('p3','queue')
    get('Lista espera ordem e posição','Vagas',admin,f'/inscricoes/turmas/{cid}/fila/',extra={'posicoes_1_2':lambda r,b,a:'Posição 1' in r['text'] and 'Posição 2' in r['text'],'ordem_p2_p3':lambda r,b,a:r['text'].find(RUN+' P2')<r['text'].find(RUN+' P3'),'espera_persistida':lambda r,b,a:find(a,'enrollments.Enrollment',id=e2)['status']==find(a,'enrollments.Enrollment',id=e3)['status']=='WAITLISTED'})
    get('Participante vê própria posição sem terceiros','Autorização',CLIENTS['p2'],'/inscricoes/?q='+RUN,extra={'posicao_1':lambda r,b,a:'Posição 1' in r['text'],'sem_nome_terceiro':lambda r,b,a:RUN+' P1' not in r['text'] and RUN+' P3' not in r['text']})
    post('Confirmar sem vaga bloqueado','Vagas',admin,f'/inscricoes/{e2}/confirmar/',{},n=200,unchanged=True,check={'erro_sem_vaga':lambda r,b,a:'Não há vaga disponível' in r['text']})
    for alias in ['i1','p2']:
        post('Confirmar perfil insuficiente '+alias,'Autorização',CLIENTS[alias],f'/inscricoes/{e2}/confirmar/',source='/',verify=False,n=403,unchanged=True)
    post('Cancelar inscrição alheia bloqueado','Autorização',CLIENTS['p2'],f'/inscricoes/{e1}/cancelar/',source='/',verify=False,n=403,unchanged=True)
    post('Cancelar própria e promover primeiro da fila','Vagas',CLIENTS['p1'],f'/inscricoes/{e1}/cancelar/',{},check={'cancelada':lambda r,b,a:find(a,'enrollments.Enrollment',id=e1)['status']=='CANCELLED','p2_promovido':lambda r,b,a:find(a,'enrollments.Enrollment',id=e2)['status']=='CONFIRMED','capacidade_preservada':lambda r,b,a:sum(e['status']=='CONFIRMED' and e['class_group_id']==cid for e in a['enrollments.Enrollment'])==1})
    em=ENROLLMENTS[('minor','queue')]
    post('Rejeitar exige motivo','Inscrições',admin,f'/inscricoes/{em}/rejeitar/',{},n=200,unchanged=True,check={'motivo_obrigatorio':lambda r,b,a:'Este campo é obrigatório' in r['text']})
    post('Rejeitar inscrição com histórico','Inscrições',admin,f'/inscricoes/{em}/rejeitar/',{'reason':RUN+' motivo fictício'},check={'rejeitada':lambda r,b,a:find(a,'enrollments.Enrollment',id=em)['status']=='REJECTED','historico_novo':lambda r,b,a:len(a['enrollments.EnrollmentStatusHistory'])==len(b['enrollments.EnrollmentStatusHistory'])+1})
    post('Cancelamento administrativo exige motivo','Inscrições',admin,f'/inscricoes/{e2}/cancelar/',{},n=200,unchanged=True,check={'motivo_obrigatorio':lambda r,b,a:'Este campo é obrigatório' in r['text']})
    post('Cancelar confirmado por administrador','Vagas',admin,f'/inscricoes/{e2}/cancelar/',{'reason':RUN+' cancelamento'},check={'p3_promovido':lambda r,b,a:find(a,'enrollments.Enrollment',id=e3)['status']=='CONFIRMED'})
    # Two isolated administrators' sessions, at most two simultaneous POSTs, one exclusive last seat.
    ra=request_enrollment('p1','race');rb=request_enrollment('p2','race');before=snapshot();first=len(REQUESTS)
    race_clients=[];payloads=[]
    for eid in [ra,rb]:
        c=Session('ADMIN_CONCURRENCY');c.post('/entrar/',{'username':CREDS['admin']['email'],'password':CREDS['admin']['password']});page=c.request(f'/inscricoes/{eid}/confirmar/');token=next(f['fields']['csrfmiddlewaretoken'] for f in Forms(page['text']).forms if 'reason' in f['names']);race_clients.append(c);payloads.append({'reason':'','csrfmiddlewaretoken':token})
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        results=list(ex.map(lambda args:args[0].request(f'/inscricoes/{args[1]}/confirmar/','POST',args[2]),zip(race_clients,[ra,rb],payloads)))
    after=snapshot();occupied=sum(e['class_group_id']==CLASSES['race'] and e['status']=='CONFIRMED' for e in after['enrollments.Enrollment'])
    ok=occupied==1 and sorted(r['status'] for r in results)==[200,302] and len(after['enrollments.EnrollmentStatusHistory'])==len(before['enrollments.EnrollmentStatusHistory'])+1
    CASES.append({'id':f'HTTP-{len(CASES)+1:03d}','functionality':'Concorrência última vaga (duas requisições)','group':'Vagas','endpoint':f'/inscricoes/<race-enrollment>/confirmar/','method':'POST x2','profile':'ADMIN','preconditions':{'capacity':1,'pending':2,'class_id':CLASSES['race']},'expected':'Uma confirmação e uma rejeição de formulário; ocupação <= 1','observed':f'HTTP {[r["status"] for r in results]}; confirmadas={occupied}','status':[r['status'] for r in results],'checks':{'uma_confirmacao':ok},'classification':'APROVADO' if ok else 'REPROVADO','timestamp':datetime.now(TZ).isoformat(),'requests':list(range(first+1,len(REQUESTS)+1)),'persisted_effects':changes(before,after)});save();print(CASES[-1]['id'],CASES[-1]['classification'],'Concorrência última vaga',flush=True)

def academic(admin):
    cid=CLASSES['academic'];instructor=CLIENTS['i1']
    for alias in ['p1','p2','p3','minor']:
        eid=request_enrollment(alias,'academic',admin=(alias=='minor'))
        post('Confirmar acadêmica '+alias,'Inscrições',admin,f'/inscricoes/{eid}/confirmar/',{},check={'confirmada':lambda r,b,a,eid=eid:find(a,'enrollments.Enrollment',id=eid)['status']=='CONFIRMED'})
    post('Iniciar turma acadêmica','Turmas',admin,f'/oficinas/turmas/{cid}/situacao/in_progress/',source=f'/oficinas/turmas/{cid}/',check={'em_andamento':lambda r,b,a:find(a,'workshops.ClassGroup',id=cid)['status']=='IN_PROGRESS'})
    path=f'/acompanhamento/turmas/{cid}/conclusao/'
    post('Conclusão com encontros pendentes bloqueada','Conclusão',admin,path,source=f'/acompanhamento/turmas/{cid}/frequencia/',unchanged=True,check={'continua_andamento':lambda r,b,a:find(a,'workshops.ClassGroup',id=cid)['status']=='IN_PROGRESS'})
    for alias,n in [('i2',404),('p1',403)]:get('Frequência turma sem autorização '+alias,'Autorização',CLIENTS[alias],f'/acompanhamento/turmas/{cid}/frequencia/',n)
    def attendance_data(states):
        data={'form-TOTAL_FORMS':'4','form-INITIAL_FORMS':'4','form-MIN_NUM_FORMS':'1','form-MAX_NUM_FORMS':'1000'}
        for i,alias in enumerate(['minor','p1','p2','p3']):
            data[f'form-{i}-enrollment_id']=ENROLLMENTS[(alias,'academic')];data[f'form-{i}-status']=states[alias];data[f'form-{i}-note']=RUN+' frequência fictícia'
        return data
    all_present={a:'PRESENT' for a in ['minor','p1','p2','p3']}
    for alias in ['i2','p1']:
        post('Chamada não autorizada '+alias,'Autorização',CLIENTS[alias],f'/acompanhamento/encontros/{MEETINGS[0]}/chamada/',attendance_data(all_present),source='/',verify=False,n=403,unchanged=True)
    post('Chamada encontro futuro bloqueada','Frequência',instructor,f'/acompanhamento/encontros/{GLOBALS["future"]}/chamada/',attendance_data(all_present),n=200,unchanged=True,check={'erro_apos_termino':lambda r,b,a:'após o término' in r['text']})
    for i,mid in enumerate(MEETINGS):
        states={'p1':'ABSENT' if i==3 else 'PRESENT','p2':'PRESENT' if i<2 else ('JUSTIFIED' if i==2 else 'ABSENT'),'p3':'PRESENT','minor':'PRESENT'}
        post('Registrar presença/ausência encontro '+str(i+1),'Frequência',instructor,f'/acompanhamento/encontros/{mid}/chamada/',attendance_data(states),check={'quatro_registros':lambda r,b,a,mid=mid:len([x for x in a['learning.Attendance'] if x['meeting_id']==mid])==4,'encontro_realizado':lambda r,b,a,mid=mid:find(a,'workshops.Meeting',id=mid)['status']=='COMPLETED'})
    mid=MEETINGS[0];states={'minor':'PRESENT','p1':'PRESENT','p2':'PRESENT','p3':'ABSENT'}
    post('Corrigir chamada sem duplicidade','Frequência',admin,f'/acompanhamento/encontros/{mid}/chamada/',attendance_data(states),check={'sem_duplicidade':lambda r,b,a:len(a['learning.Attendance'])==len(b['learning.Attendance']),'autor_e_horario_atualizados':lambda r,b,a:find(a,'learning.Attendance',meeting_id=mid,enrollment_id=ENROLLMENTS[('p3','academic')])['recorded_by_id']!=find(b,'learning.Attendance',meeting_id=mid,enrollment_id=ENROLLMENTS[('p3','academic')])['recorded_by_id']})
    states['p3']='PRESENT'
    post('Restabelecer chamada exclusiva de teste','Frequência',instructor,f'/acompanhamento/encontros/{mid}/chamada/',attendance_data(states),check={'p3_presente':lambda r,b,a:find(a,'learning.Attendance',meeting_id=mid,enrollment_id=ENROLLMENTS[('p3','academic')])['status']=='PRESENT','sem_duplicidade':lambda r,b,a:len(a['learning.Attendance'])==16})
    get('Percentuais turma 75/50/100','Frequência',instructor,f'/acompanhamento/turmas/{cid}/frequencia/',extra={'percentuais_renderizados':lambda r,b,a:all(x in r['text'] for x in ['75,00%','50,00%','100,00%'])})
    get('Participante somente própria frequência','Autorização',CLIENTS['p1'],'/acompanhamento/frequencia/',extra={'75_porcento':lambda r,b,a:'75,00%' in r['text'],'sem_nomes_terceiros':lambda r,b,a:all(RUN+' '+x not in r['text'] for x in ['P2','P3','MINOR'])})
    # Cancel the future meeting through HTTP so it is excluded from completion/workload.
    post('Cancelar encontro futuro','Encontros',admin,f'/oficinas/encontros/{GLOBALS["future"]}/cancelar/',source=f'/oficinas/turmas/{cid}/',check={'cancelado':lambda r,b,a:find(a,'workshops.Meeting',id=GLOBALS['future'])['status']=='CANCELLED'})
    post('Chamada encontro cancelado bloqueada','Frequência',instructor,f'/acompanhamento/encontros/{GLOBALS["future"]}/chamada/',attendance_data(all_present),source='/',verify=False,n=403,unchanged=True)
    post('Conclusão sem avaliações bloqueada','Conclusão',admin,path,source=f'/acompanhamento/turmas/{cid}/frequencia/',unchanged=True,check={'situacoes_preservadas':lambda r,b,a:all(e['status']=='CONFIRMED' for e in a['enrollments.Enrollment'] if e['class_group_id']==cid)})
    for alias in ['p1','p2','p3']:
        eid=ENROLLMENTS[(alias,'academic')];p=f'/acompanhamento/inscricoes/{eid}/projeto/'
        data={'title':RUN+' PROJECT_'+alias.upper(),'description':RUN+' entrega fictícia','repository_url':'https://example.com/'+RUN.lower(),'is_delivered':'on'}
        if alias=='p1':
            post('Projeto URL inválida','Projetos',CLIENTS[alias],p,data|{'repository_url':'not a url'},n=200,unchanged=True,check={'erro_url':lambda r,b,a:'errorlist' in r['text'] and 'url' in r['text'].lower() and 'válid' in r['text'].lower()})
            post('Salvar projeto rascunho','Projetos',CLIENTS[alias],p,data|{'is_delivered':''},check={'rascunho_sem_data_entrega':lambda r,b,a:not find(a,'learning.StudentProject',enrollment_id=eid)['is_delivered'] and find(a,'learning.StudentProject',enrollment_id=eid)['delivered_at'] is None})
        post('Entregar projeto '+alias,'Projetos',CLIENTS[alias],p,data,check={'entregue_com_data':lambda r,b,a,eid=eid:find(a,'learning.StudentProject',enrollment_id=eid)['is_delivered'] and find(a,'learning.StudentProject',enrollment_id=eid)['delivered_at'] is not None})
    eid=ENROLLMENTS[('p1','academic')];project=find(snapshot(),'learning.StudentProject',enrollment_id=eid)['id']
    get('Projeto de terceiro bloqueado','Autorização',CLIENTS['p2'],f'/acompanhamento/inscricoes/{eid}/projeto/',404)
    post('Projeto de terceiro POST bloqueado','Autorização',CLIENTS['p2'],f'/acompanhamento/inscricoes/{eid}/projeto/',{'title':RUN+' UNAUTHORIZED'},source='/',verify=False,n=404,unchanged=True)
    post('Revisar projeto instrutor vinculado','Projetos',instructor,f'/acompanhamento/projetos/{project}/revisao/',{'review_notes':RUN+' revisão'},check={'revisao_persistida':lambda r,b,a:find(a,'learning.StudentProject',id=project)['review_notes']==RUN+' revisão'})
    post('Revisão por instrutor alheio bloqueada','Autorização',CLIENTS['i2'],f'/acompanhamento/projetos/{project}/revisao/',{'review_notes':RUN+' BAD'},source='/',verify=False,n=403,unchanged=True)
    for alias in ['p1','p2','p3','minor']:
        eid=ENROLLMENTS[(alias,'academic')];p=f'/acompanhamento/inscricoes/{eid}/avaliacao/'
        if alias=='p1':
            post('Nota 10,1 bloqueada','Avaliações',instructor,p,{'final_score':'10.1','feedback':RUN+' inválida'},n=200,unchanged=True,check={'erro_nota':lambda r,b,a:'errorlist' in r['text']})
        score={'p1':'6.0','p2':'10.0','p3':'5.9','minor':'10.0'}[alias]
        data={'final_score':score,'feedback':RUN+' FEEDBACK_'+alias.upper()}
        post('Avaliar sem publicar '+alias,'Avaliações',instructor,p,data,check={'nota_persistida':lambda r,b,a,eid=eid,score=score:find(a,'learning.Evaluation',enrollment_id=eid)['final_score']==score,'resultado_privado':lambda r,b,a,eid=eid:find(a,'learning.Evaluation',enrollment_id=eid)['published_at'] is None})
        if alias=='p1':
            get('Devolutiva não publicada oculta','Avaliações',CLIENTS['p1'],'/acompanhamento/frequencia/',extra={'feedback_oculto':lambda r,b,a:RUN+' FEEDBACK_P1' not in r['text'],'mensagem_aguardando':lambda r,b,a:'Aguardando publicação' in r['text']})
        post('Publicar avaliação '+alias,'Avaliações',instructor,p,data|{'publish':'on'},check={'publicada':lambda r,b,a,eid=eid:find(a,'learning.Evaluation',enrollment_id=eid)['published_at'] is not None})
    eid=ENROLLMENTS[('p1','academic')]
    get('Devolutiva publicada visível','Avaliações',CLIENTS['p1'],'/acompanhamento/frequencia/',extra={'feedback_visivel':lambda r,b,a:RUN+' FEEDBACK_P1' in r['text']})
    for alias in ['i2','p1']:
        post('Avaliação perfil/vínculo inválido '+alias,'Autorização',CLIENTS[alias],f'/acompanhamento/inscricoes/{eid}/avaliacao/',{'final_score':'0','feedback':RUN+' BAD'},source='/',verify=False,n=403,unchanged=True)
    # Generic transition must not bypass academic validation.
    post('Conclusão genérica não contorna critérios','Conclusão',admin,f'/oficinas/turmas/{cid}/situacao/completed/',source='/',verify=False,unchanged=True,check={'permanece_andamento':lambda r,b,a:find(a,'workshops.ClassGroup',id=cid)['status']=='IN_PROGRESS'})
    post('Processar conclusão 1 aprovado / 3 não concluintes','Conclusão',admin,path,source=f'/acompanhamento/turmas/{cid}/frequencia/',check={'turma_concluida':lambda r,b,a:find(a,'workshops.ClassGroup',id=cid)['status']=='COMPLETED','p1_aprovado_limite_75_nota6':lambda r,b,a:find(a,'enrollments.Enrollment',id=ENROLLMENTS[('p1','academic')])['status']=='APPROVED','p2_frequencia_insuficiente':lambda r,b,a:find(a,'enrollments.Enrollment',id=ENROLLMENTS[('p2','academic')])['status']=='NOT_COMPLETED','p3_nota_insuficiente':lambda r,b,a:find(a,'enrollments.Enrollment',id=ENROLLMENTS[('p3','academic')])['status']=='NOT_COMPLETED','menor_sem_projeto':lambda r,b,a:find(a,'enrollments.Enrollment',id=ENROLLMENTS[('minor','academic')])['status']=='NOT_COMPLETED'})
    for endpoint in [f'/acompanhamento/inscricoes/{eid}/projeto/',f'/acompanhamento/inscricoes/{eid}/avaliacao/']:
        get('Alteração após conclusão bloqueada','Conclusão',CLIENTS['p1'] if endpoint.endswith('projeto/') else instructor,endpoint,403)
    certificates(admin)

def certificates(admin):
    eid=ENROLLMENTS[('p1','academic')];bad=ENROLLMENTS[('p2','academic')]
    get('Listar certificados','Certificados',CLIENTS['p1'],'/acompanhamento/certificados/')
    post('Certificado não concluinte bloqueado','Certificados',admin,f'/acompanhamento/inscricoes/{bad}/certificado/emitir/',source='/',verify=False,unchanged=True,check={'sem_certificado':lambda r,b,a:not any(c['enrollment_id']==bad for c in a['learning.Certificate'])})
    post('Emitir certificado elegível','Certificados',admin,f'/acompanhamento/inscricoes/{eid}/certificado/emitir/',source='/acompanhamento/certificados/',check={'certificado_novo_4h':lambda r,b,a:find(a,'learning.Certificate',enrollment_id=eid)['workload_hours']=='4.00'})
    cert=find(snapshot(),'learning.Certificate',enrollment_id=eid);GLOBALS['certificate']=cert['id'];path=f'/acompanhamento/certificados/{cert["id"]}/'
    get('Consultar certificado próprio','Certificados',CLIENTS['p1'],path,extra={'nome_turma_carga':lambda r,b,a:RUN+' P1' in r['text'] and class_code('academic') in r['text'] and '4,00' in r['text']})
    r,_=get('Baixar PDF próprio e conferir conteúdo','Certificados',CLIENTS['p1'],path+'baixar/',extra={'mime_pdf':lambda r,b,a:r['headers'].get('Content-Type')=='application/pdf','assinatura_pdf':lambda r,b,a:r['body'].startswith(b'%PDF') and len(r['body'])>500,'nome_oficina_turma':lambda r,b,a:all(v.encode() in r['body'] for v in [RUN+' P1',RUN+' WORKSHOP',class_code('academic'),cert['verification_code']]),'carga4h':lambda r,b,a:b'4,00 horas' in r['body']})
    # PDF contains synthetic names only; sanitized evidence preserves fingerprint and checked attributes.
    (OUT/'pdf-evidencia.json').write_text(json.dumps({'endpoint':path+'baixar/','bytes':len(r['body']),'sha256':hashlib.sha256(r['body']).hexdigest(),'synthetic_only':True,'verified':['signature','mime','name','workshop','class','workload','verification_code']},indent=2))
    for alias,n in [('i1',200),('i2',404),('p2',404)]:
        get('Permissão certificado '+alias,'Autorização',CLIENTS[alias],path,n)
        get('Permissão download certificado '+alias,'Autorização',CLIENTS[alias],path+'baixar/',n)
    post('Emissão repetida idempotente','Certificados',admin,f'/acompanhamento/inscricoes/{eid}/certificado/emitir/',source='/',verify=False,unchanged=True,check={'um_certificado':lambda r,b,a:len(a['learning.Certificate'])==1})
    post('Revogação exige motivo','Certificados',admin,path+'revogar/',{},source=path,unchanged=True,check={'ainda_ativo':lambda r,b,a:find(a,'learning.Certificate',id=cert['id'])['is_active']})
    post('Revogar certificado desta execução','Certificados',admin,path+'revogar/',{'reason':RUN+' revogação de teste'},source=path,check={'revogado_com_historico':lambda r,b,a:not find(a,'learning.Certificate',id=cert['id'])['is_active'] and find(a,'learning.Certificate',id=cert['id'])['revoked_at'] is not None})
    get('PDF revogado bloqueado','Certificados',CLIENTS['p1'],path+'baixar/',404)
    get('Certificado revogado oculto ao participante','Certificados',CLIENTS['p1'],path,404)
    get('Histórico certificado revogado consultável ao admin','Certificados',admin,path)
    post('Reemissão de revogado bloqueada','Certificados',admin,f'/acompanhamento/inscricoes/{eid}/certificado/emitir/',source='/',verify=False,unchanged=True,check={'segue_revogado':lambda r,b,a:not find(a,'learning.Certificate',id=cert['id'])['is_active']})

def reports(admin):
    query=urllib.parse.urlencode({'workshop':GLOBALS['workshop'],'class_status':'COMPLETED','period_start':GLOBALS['today'].isoformat(),'period_end':GLOBALS['today'].isoformat()})
    r,_=get('Painel filtros e indicadores reconciliados','Painéis',admin,'/painel/?'+query,extra={'uma_turma':lambda r,b,a:'Turmas</small><strong>1' in r['text'],'quatro_inscricoes':lambda r,b,a:'Inscrições</small><strong>4' in r['text'],'ocupacao100':lambda r,b,a:'Ocupação</small><strong>100,00%' in r['text'],'frequencia_media81_25':lambda r,b,a:'Frequência média</small><strong>81,25%' in r['text'],'aprovacao25':lambda r,b,a:'Taxa de aprovação</small><strong>25,00%' in r['text'],'projetos3':lambda r,b,a:'Projetos entregues</small><strong>3' in r['text'],'outros_fora_tabela':lambda r,b,a:class_code('queue') not in r['text'] and 'DEMO-' not in r['text']})
    for alias in ['i1','i2']:
        get('Painel instrutor isolado '+alias,'Painéis',CLIENTS[alias],'/painel/',extra={'sem_csv':lambda r,b,a:'Inscrições CSV' not in r['text'],'somente_proprias':lambda r,b,a,alias=alias:(class_code('other') not in r['text'] if alias=='i1' else class_code('academic') not in r['text'])})
    get('Participante sem painel gerencial','Painéis',CLIENTS['p1'],'/painel/',403)
    for kind,columns in [('inscricoes',['Participante','Oficina','Turma','Situação','Data da inscrição','Motivo da situação']),('frequencia',['Participante','Oficina','Turma','Encontros realizados','Presenças','Ausências','Faltas justificadas','Frequência']),('conclusao',['Participante','Oficina','Turma','Período','Resultado','Nota final','Projeto entregue','Certificado ativo','Motivo'])]:
        def valid_csv(r,b,a,columns=columns,kind=kind):
            parsed=list(csv.reader(io.StringIO(r['body'].decode('utf-8-sig')),delimiter=';'))
            if parsed[4]!=columns or len(parsed[5:])!=4:return False
            if any(row[2]!=class_code('academic') for row in parsed[5:]):return False
            if any(x in r['text'].lower() for x in ['cpf','telefone','@validation.']):return False
            if SYNTHETIC['cpf'] in r['text']:return False
            if kind=='frequencia':return sorted(row[-1] for row in parsed[5:])==['100,00%','100,00%','50,00%','75,00%']
            if kind=='conclusao':return sum(row[4]=='Aprovada' for row in parsed[5:])==1 and all(row[7]=='Não' for row in parsed[5:])
            return True
        r,_=get('CSV '+kind+' filtros/cabeçalhos/conteúdo','CSV',admin,f'/painel/relatorios/{kind}.csv?'+query,extra={'mime_csv':lambda r,b,a:r['headers'].get('Content-Type')=='text/csv; charset=utf-8','csv_conferido_sem_dados_protegidos':valid_csv})
        parsed=list(csv.reader(io.StringIO(r['body'].decode('utf-8-sig')),delimiter=';'))
        (OUT/('csv-'+kind+'-evidencia.json')).write_text(json.dumps({'header':parsed[4],'data_rows':len(parsed[5:]),'sha256':hashlib.sha256(r['body']).hexdigest(),'filters':{'workshop_id':GLOBALS['workshop'],'class_status':'COMPLETED'},'contains_protected_fields':False},indent=2,ensure_ascii=False))
        for alias in ['i1','p1']:get('CSV '+kind+' acesso negado '+alias,'Autorização',CLIENTS[alias],f'/painel/relatorios/{kind}.csv?'+query,403)
    get('CSV filtro inválido','CSV',admin,'/painel/relatorios/inscricoes.csv?period_start=2026-10-15&period_end=2026-10-01',400)
    get('Relatório inexistente','CSV',admin,'/painel/relatorios/desconhecido.csv',404)
    get('Painel filtro inválido sem dados','Painéis',admin,'/painel/?period_start=2026-10-15&period_end=2026-10-01',extra={'erro_visivel':lambda r,b,a:'data inicial' in r['text'],'universo_vazio':lambda r,b,a:'Turmas</small><strong>0' in r['text']})

def recovery(creds):
    anon=Session('ANONYMOUS_PASSWORD_RESET')
    post('Recuperação e-mail inválido','Recuperação',anon,'/senha/recuperar/',{'email':'bad email'},n=200,unchanged=True,check={'erro_formulario':lambda r,b,a:'field-error' in r['text']})
    started=datetime.now().astimezone().isoformat()
    post('Processar recuperação conta exclusiva','Recuperação',anon,'/senha/recuperar/',{'email':creds['p3']['email']},unchanged=True,check={'pagina_confirmacao':lambda r,b,a:r['headers'].get('Location')=='/senha/recuperar/enviado/'})
    get('Página confirmação recuperação','Recuperação',anon,'/senha/recuperar/enviado/')
    raw=subprocess.run(COMPOSE+['logs','--no-color','--since',started,'app'],capture_output=True,text=True,timeout=20)
    # Never save or print logs: they may contain mail addresses and recovery tokens.
    console_ok=creds['p3']['email'] in raw.stdout and BASE+'/senha/redefinir/' in raw.stdout
    case={'id':f'HTTP-{len(CASES)+1:03d}','functionality':'E-mail de recuperação gerado no console','group':'Recuperação','endpoint':'/senha/recuperar/','method':'POST (evidência complementar de log sanitizada)','profile':'ANONYMOUS','preconditions':{'synthetic_account':True},'expected':'Mensagem para conta fictícia e URL HTTPS do domínio; não comprova entrega SMTP','observed':'Mensagem de console conferida em memória; conteúdo e token não preservados','status':None,'checks':{'console_email_correct_target_https':console_ok},'classification':'APROVADO' if console_ok else 'REPROVADO','timestamp':datetime.now(TZ).isoformat()}
    CASES.append(case);save();print(case['id'],case['classification'],case['functionality'],flush=True)

GLOBALS={};PARTICIPANTS={};INSTRUCTORS={};CLASSES={};ENROLLMENTS={};PEOPLE_DATA={};CLASS_DATA={};MEETINGS=[];SYNTHETIC={}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',required=True,type=Path)
    parser.add_argument('--run-id')
    parser.add_argument('--resume-after',choices=['people'])
    args=parser.parse_args();RUN=args.run_id or datetime.now(TZ).strftime('VALIDATION-%Y%m%d-%H%M%S')
    if not re.fullmatch(r'VALIDATION-\d{8}-\d{6}',RUN):raise SystemExit('Identificador inválido')
    OUT=ROOT/'docs/06-testes/validacao-publicada'/RUN;OUT.mkdir(parents=True,exist_ok=True)
    PRIVATE=args.private_dir;PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(PRIVATE,0o700)
    CREDS=None
    original_prep=prep
    def prep():
        global CREDS
        CREDS=original_prep();return CREDS
    try:
        if args.resume_after:
            CREDS=json.loads((PRIVATE/'credentials.json').read_text());CASES.extend(json.loads((OUT/'matriz.json').read_text()));REQUESTS.extend(json.loads((OUT/'requisicoes.json').read_text()))
            for alias in CREDS:login(alias,CREDS)
            s=snapshot()
            for alias in ['p1','p2','p3','minor']:PARTICIPANTS[alias]=find(s,'people.Participant',full_name=RUN+' '+alias.upper())['id']
            for alias in ['i1','i2']:
                user=find(s,'accounts.User',full_name=RUN+' '+alias.upper())['id'];INSTRUCTORS[alias]=find(s,'people.Instructor',user_id=user)['id']
            GLOBALS['guardian']=find(s,'people.Guardian',full_name=RUN+' GUARDIAN_EDITED')['id'];GLOBALS['institution']=find(s,'people.Institution',name=RUN+' INSTITUTION')['id']
            SYNTHETIC['cpf']=orm("from apps.people.models import Participant\nprint(json.dumps(Participant.objects.get(pk=%r).cpf))" % PARTICIPANTS['p1'])
            workshops(CLIENTS['admin']);enrollments(CLIENTS['admin']);academic(CLIENTS['admin']);reports(CLIENTS['admin']);recovery(CREDS)
            c=CLIENTS['p3'];get('Logout por GET rejeitado','Autenticação',c,'/sair/',405);post('Logout por POST','Autenticação',c,'/sair/',source='/',unchanged=True,check={'redirect_login':lambda r,b,a:r['headers'].get('Location')=='/entrar/'});get('Acesso após logout','Autenticação',c,'/',302)
        else:main()
    finally:
        save();(OUT/'estado-final-execucao.json').write_text(json.dumps(snapshot(),indent=2,ensure_ascii=False))
        (OUT/'dados-existentes-final-hashes.json').write_text(json.dumps(existing_hash(),indent=2))
        (OUT/'ids-execucao.json').write_text(json.dumps({m:[r['id'] for r in records] for m,records in snapshot().items()},indent=2))
        print('Resumo:',json.dumps({k:sum(c['classification']==k for c in CASES) for k in ['APROVADO','REPROVADO','BLOQUEADO','NÃO EXECUTADO']}),flush=True)
