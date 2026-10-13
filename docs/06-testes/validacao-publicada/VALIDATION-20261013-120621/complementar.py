#!/usr/bin/env python3
"""Complemento autorizado após validar.py. Usa a mesma execução e credenciais privadas.
python3 complementar.py --private-dir /diretorio/restrito --run-id VALIDATION-...
Não execute simultaneamente ao script principal.
"""
import argparse
import json
import os
import re
import secrets
import subprocess
from datetime import datetime,timedelta
from pathlib import Path
import validar as v

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--private-dir',required=True,type=Path);parser.add_argument('--run-id',required=True);a=parser.parse_args()
    v.RUN=a.run_id;v.PRIVATE=a.private_dir;v.OUT=v.ROOT/'docs/06-testes/validacao-publicada'/v.RUN
    v.CASES=json.loads((v.OUT/'matriz.json').read_text());v.REQUESTS=json.loads((v.OUT/'requisicoes.json').read_text());v.CREDS=json.loads((a.private_dir/'credentials.json').read_text())
    admin=v.login('admin',v.CREDS);p1=v.login('p1',v.CREDS);p2=v.login('p2',v.CREDS);p3=v.login('p3',v.CREDS);i1=v.login('i1',v.CREDS);v.login('i2',v.CREDS)
    s=v.snapshot();run=v.RUN;today=datetime.now(v.TZ).date()
    ids={alias:v.find(s,'accounts.User',full_name=run+' '+alias.upper())['id'] for alias in ['admin','p1','p2','p3','minor','i1','i2']}
    participants={alias:v.find(s,'people.Participant',user_id=ids[alias])['id'] for alias in ['p1','p2','p3','minor']}
    classes={alias:v.find(s,'workshops.ClassGroup',code=v.class_code(alias))['id'] for alias in ['queue','academic','race','other']}
    v.GLOBALS['workshop']=v.find(s,'workshops.Workshop',slug=run.lower())['id'];v.GLOBALS['today']=today
    # Context lost when the original executor resumed: reread only the synthetic value
    # into memory, then repeat the CSV checks without persisting the identifier.
    v.SYNTHETIC['cpf']=v.orm("from apps.people.models import Participant\nprint(json.dumps(Participant.objects.get(pk=%r).cpf))" % participants['p1'])
    for f in v.OUT.glob('csv-*-evidencia.json'):
        (v.OUT/(f.stem+'-primeira-passagem.json')).write_text(f.read_text())
    v.reports(admin)
    cert=s['learning.Certificate'][0];cert_path=f'/acompanhamento/certificados/{cert["id"]}/'
    v.get('Reteste download revogado oculto ao titular','Certificados',p1,cert_path+'baixar/',404)
    v.get('Reteste consulta revogada oculta ao titular','Certificados',p1,cert_path,404)
    v.get('Histórico revogado preservado para administrador','Certificados',admin,cert_path,extra={'revogacao_registrada':lambda r,b,a:'REVOGADO' in r['text'] and run+' revogação de teste' in r['text']})
    v.get('Administrador também não baixa PDF revogado','Certificados',admin,cert_path+'baixar/',403)
    inventory=v.orm('''
from django.urls import get_resolver,URLPattern,URLResolver
out=[]
def walk(patterns,prefix=''):
 for p in patterns:
  path=prefix+str(p.pattern)
  if isinstance(p,URLResolver):
   if not path.startswith('admin/'): walk(p.url_patterns,path)
  else:
   cls=getattr(p.callback,'view_class',None)
   methods=[m.upper() for m in ['get','post','put','patch','delete'] if cls and hasattr(cls,m)]
   out.append({'pattern':path,'name':p.name,'view':cls.__name__ if cls else p.callback.__name__,'methods':methods or ['function_view']})
walk(get_resolver().url_patterns)
print(json.dumps(out))
''')
    (v.OUT/'endpoints-descobertos.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False))
    v.get('RF-006: acesso à edição do próprio perfil','Perfil próprio',p1,'/',extra={'entrada_para_perfil_proprio':lambda r,b,a:bool(re.search(r'href="[^"]*(?:perfil|profile|conta)[^"]*"',r['text']))},)
    v.post('Turma concluída bloqueia novo encontro','Encontros',admin,f'/oficinas/turmas/{classes["academic"]}/encontros/novo/',{'title':run+' DUP_REPRO','starts_at':today.isoformat()+'T00:00','ends_at':today.isoformat()+'T01:00'},source='/',verify=False,n=403,unchanged=True)
    # Completed-class guard above cannot reproduce the original duplicate, so use a
    # separate open class below; preserve the original 500 as its own evidence.
    # Account lifecycle through UserAdmin, preserving password and only touching our account.
    def user_data(active=True):
        data={'email':v.CREDS['p3']['email'],'full_name':run+' P3','role':'PARTICIPANT','_save':'Salvar'}
        if active:data['is_active']='on'
        return data
    path=f'/admin/accounts/user/{ids["p3"]}/change/'
    v.get('Consultar conta de validação no admin','Usuários',admin,path)
    v.post('Desativar usuário exclusivo','Usuários',admin,path,user_data(False),check={'inativo_persistido':lambda r,b,a:not v.find(a,'accounts.User',id=ids['p3'])['is_active']})
    anon=v.Session('ANONYMOUS_INACTIVE_USER')
    v.post('Login usuário inativo rejeitado','Autenticação',anon,'/entrar/',{'username':v.CREDS['p3']['email'],'password':v.CREDS['p3']['password']},n=200,unchanged=True,check={'erro_generico':lambda r,b,a:'E-mail ou senha inválidos' in r['text'],'sem_sessao':lambda r,b,a:not any(c.name=='sessionid' for c in anon.jar)})
    v.get('Sessão anterior de usuário desativado perde acesso','Autenticação',p3,'/',302,{'destino_login':lambda r,b,a:r['headers'].get('Location','').startswith('/entrar/?next=')})
    v.post('Reativar usuário exclusivo','Usuários',admin,path,user_data(True),check={'ativo_persistido':lambda r,b,a:v.find(a,'accounts.User',id=ids['p3'])['is_active']})
    v.login('p3',v.CREDS)
    instructor=v.find(v.snapshot(),'people.Instructor',user_id=ids['i1'])['id']
    v.post('Editar perfil instrutor','Pessoas',admin,f'/pessoas/instrutores/{instructor}/editar/',{'user':ids['i1'],'biography':run+' biografia editada','specialties':'Python, HTTP','is_active':'on'},check={'especialidade_editada':lambda r,b,a:v.find(a,'people.Instructor',id=instructor)['specialties']=='Python, HTTP'})
    # Enrollment eligibility. Updating only our spare participant and restoring it via HTTP.
    profile_path=f'/pessoas/participantes/{participants["p3"]}/editar/'
    profile={'user':ids['p3'],'full_name':run+' P3','birth_date':f'{today.year-19}-01-01','is_active':'on'}
    v.post('Preparar idade fora da faixa em perfil exclusivo','Preparação HTTP',admin,profile_path,profile|{'birth_date':f'{today.year-22}-01-01'},check={'registro_editado':lambda r,b,a:r['status']==302})
    enroll_path=f'/inscricoes/turmas/{classes["other"]}/solicitar/'
    v.post('Inscrição fora faixa etária bloqueada','Inscrições',v.CLIENTS['p3'],enroll_path,source='/inscricoes/turmas-disponiveis/',unchanged=True,check={'sem_inscricao_nova':lambda r,b,a:len(a['enrollments.Enrollment'])==len(b['enrollments.Enrollment'])})
    v.post('Restabelecer idade fictícia válida','Preparação HTTP',admin,profile_path,profile,check={'editado':lambda r,b,a:r['status']==302})
    v.post('Desativar perfil participante exclusivo','Pessoas',admin,profile_path,profile|{'is_active':''},check={'perfil_inativo':lambda r,b,a:not v.find(a,'people.Participant',id=participants['p3'])['is_active']})
    v.post('Inscrição participante inativo bloqueada','Inscrições',v.CLIENTS['p3'],enroll_path,source='/',verify=False,unchanged=True,check={'sem_nova_inscricao':lambda r,b,a:len(a['enrollments.Enrollment'])==len(b['enrollments.Enrollment'])})
    v.post('Reativar perfil exclusivo','Pessoas',admin,profile_path,profile,check={'perfil_ativo':lambda r,b,a:v.find(a,'people.Participant',id=participants['p3'])['is_active']})
    e=v.find(v.snapshot(),'enrollments.Enrollment',participant_id=participants['p1'],class_group_id=classes['academic'])['id']
    v.post('Cancelamento de inscrição já concluída bloqueado','Inscrições',p1,f'/inscricoes/{e}/cancelar/',source='/',verify=False,n=200,unchanged=True,check={'formulario_erro':lambda r,b,a:'não pode mais ser cancelada' in r['text']})
    v.get('Fila administrativa inacessível ao participante','Autorização',p2,f'/inscricoes/turmas/{classes["queue"]}/fila/',403)
    v.get('Fila de turma alheia inacessível ao instrutor','Autorização',i1,f'/inscricoes/turmas/{classes["other"]}/fila/',404)
    v.get('Filtrar inscrições por situação','Inscrições',admin,'/inscricoes/?q='+run+'&status=APPROVED',extra={'somente_aprovado':lambda r,b,a:v.class_code('academic') in r['text'] and v.class_code('queue') not in r['text'],'nome_aprovado':lambda r,b,a:run+' P1' in r['text'] and run+' P2' not in r['text']})
    v.get('Instrutor lista inscrições próprias','Autorização',i1,'/inscricoes/?q='+run,extra={'terceira_oculta':lambda r,b,a:v.class_code('other') not in r['text']})
    # Dedicated small class for manual waitlist promotion and disabled-waitlist behavior.
    workshop=v.find(s,'workshops.Workshop',slug=run.lower())['id'];institution=s['people.Institution'][0]['id']
    for alias,waitlist in [('MANUAL',True),('NO-WAITLIST',False),('EXPIRED',True),('STARTED',True)]:
        data={'workshop':workshop,'institution':institution,'code':v.class_code(alias),'title':run+' '+alias,'location':run+' sala','capacity':'1','registration_opens_at':(today-timedelta(days=3)).isoformat()+'T00:00','registration_closes_at':(today-timedelta(days=1) if alias=='EXPIRED' else today).isoformat()+'T23:00','start_date':(today+timedelta(days=1)).isoformat(),'end_date':(today+timedelta(days=3)).isoformat()}
        if waitlist:data['waitlist_enabled']='on'
        if alias=='STARTED':data['start_date']=today.isoformat()
        v.post('Criar turma complementar '+alias,'Preparação HTTP',admin,'/oficinas/turmas/nova/',data,check={'turma_nova':lambda r,b,a:len(a['workshops.ClassGroup'])==len(b['workshops.ClassGroup'])+1})
        cid=v.find(v.snapshot(),'workshops.ClassGroup',code=v.class_code(alias))['id']
        v.post('Vincular instrutor complementar '+alias,'Preparação HTTP',admin,f'/oficinas/turmas/{cid}/instrutores/vincular/',{'instructor':instructor,'is_lead':'on'},check={'vinculado':lambda r,b,a:bool([x for x in a['workshops.ClassInstructor'] if x['class_group_id']==cid])})
        v.post('Abrir turma complementar '+alias,'Preparação HTTP',admin,f'/oficinas/turmas/{cid}/situacao/open/',source=f'/oficinas/turmas/{cid}/',check={'aberta':lambda r,b,a:v.find(a,'workshops.ClassGroup',id=cid)['status']=='OPEN'})
        if alias=='EXPIRED':
            v.post('Inscrição fora janela bloqueada','Inscrições',p1,f'/inscricoes/turmas/{cid}/solicitar/',source='/',verify=False,unchanged=True,check={'nenhuma_inscricao_na_turma':lambda r,b,a:not any(x['class_group_id']==cid for x in a['enrollments.Enrollment'])})
            continue
        v.post('Inscrever p1 turma '+alias,'Inscrições',p1,f'/inscricoes/turmas/{cid}/solicitar/',source='/inscricoes/turmas-disponiveis/',check={'pendente':lambda r,b,a:v.find(a,'enrollments.Enrollment',class_group_id=cid,participant_id=participants['p1'])['status']=='PENDING'})
        e1=v.find(v.snapshot(),'enrollments.Enrollment',class_group_id=cid,participant_id=participants['p1'])['id']
        v.post('Confirmar vaga '+alias,'Vagas',admin,f'/inscricoes/{e1}/confirmar/',check={'confirmada':lambda r,b,a:v.find(a,'enrollments.Enrollment',id=e1)['status']=='CONFIRMED'})
        if alias=='STARTED':
            v.post('Cancelamento participante após data início bloqueado','Inscrições',p1,f'/inscricoes/{e1}/cancelar/',n=200,unchanged=True,check={'somente_admin_apos_inicio':lambda r,b,a:'Após o início da turma' in r['text']})
            meeting={'title':run+' STARTED_MEETING','starts_at':today.isoformat()+'T00:00','ends_at':today.isoformat()+'T01:00'}
            v.post('Preparar encontro para retestes de formulário','Preparação HTTP',admin,f'/oficinas/turmas/{cid}/encontros/novo/',meeting,check={'encontro_criado':lambda r,b,a:len(a['workshops.Meeting'])==len(b['workshops.Meeting'])+1})
            v.post('Iniciar turma exclusiva para retestes','Preparação HTTP',admin,f'/oficinas/turmas/{cid}/situacao/in_progress/',source=f'/oficinas/turmas/{cid}/',check={'em_andamento':lambda r,b,a:v.find(a,'workshops.ClassGroup',id=cid)['status']=='IN_PROGRESS'})
            v.post('Reteste URL de projeto inválida com erro visível','Projetos',p1,f'/acompanhamento/inscricoes/{e1}/projeto/',{'title':run+' INVALID_URL_RETEST','description':run+' fictício','repository_url':'not a url','is_delivered':'on'},n=200,unchanged=True,check={'erro_url_visivel':lambda r,b,a:'errorlist' in r['text'] and 'url' in r['text'].lower() and 'válid' in r['text'].lower()})
            v.post('Reteste nota 10,1 com erro visível','Avaliações',i1,f'/acompanhamento/inscricoes/{e1}/avaliacao/',{'final_score':'10.1','feedback':run+' inválida'},n=200,unchanged=True,check={'erro_limite_visivel':lambda r,b,a:'menor ou igual a 10' in r['text']})
            continue
        v.post('Inscrever p2 turma lotada '+alias,'Vagas',p2,f'/inscricoes/turmas/{cid}/solicitar/',source='/inscricoes/turmas-disponiveis/',check={'status_documentado':lambda r,b,a:v.find(a,'enrollments.Enrollment',class_group_id=cid,participant_id=participants['p2'])['status']==('WAITLISTED' if waitlist else 'PENDING')})
        e2=v.find(v.snapshot(),'enrollments.Enrollment',class_group_id=cid,participant_id=participants['p2'])['id']
        if not waitlist:
            v.post('Sem lista espera não excede capacidade','Vagas',admin,f'/inscricoes/{e2}/confirmar/',n=200,unchanged=True,check={'sem_vaga':lambda r,b,a:'Não há vaga disponível' in r['text']})
            continue
        minor=v.login('minor',v.CREDS)
        v.post('Inscrever segundo da fila','Vagas',minor,f'/inscricoes/turmas/{cid}/solicitar/',source='/inscricoes/turmas-disponiveis/',check={'espera':lambda r,b,a:v.find(a,'enrollments.Enrollment',class_group_id=cid,participant_id=participants['minor'])['status']=='WAITLISTED'})
        second=v.find(v.snapshot(),'enrollments.Enrollment',class_group_id=cid,participant_id=participants['minor'])['id']
        # Temporarily ineligible waitlisted profiles prevent automatic promotion; restore
        # only these profiles, then exercise the real manual promotion endpoint.
        for who in ['p2','minor']:
            payload={'user':ids[who],'full_name':run+' '+who.upper(),'birth_date':f'{today.year-(16 if who=="minor" else 19)}-01-01'}
            v.post('Preparar inelegibilidade temporária fila '+who,'Preparação HTTP',admin,f'/pessoas/participantes/{participants[who]}/editar/',payload,check={'inativo':lambda r,b,a,who=who:not v.find(a,'people.Participant',id=participants[who])['is_active']})
        v.post('Liberar vaga sem promover candidatos inelegíveis','Vagas',admin,f'/inscricoes/{e1}/cancelar/',{'reason':run+' cenário de promoção manual'},check={'vaga_livre':lambda r,b,a:not any(x['class_group_id']==cid and x['status']=='CONFIRMED' for x in a['enrollments.Enrollment'])})
        for who in ['p2','minor']:
            payload={'user':ids[who],'full_name':run+' '+who.upper(),'birth_date':f'{today.year-(16 if who=="minor" else 19)}-01-01','is_active':'on'}
            v.post('Restabelecer elegibilidade fila '+who,'Preparação HTTP',admin,f'/pessoas/participantes/{participants[who]}/editar/',payload,check={'ativo':lambda r,b,a,who=who:v.find(a,'people.Participant',id=participants[who])['is_active']})
        v.post('Promover fora ordem sem motivo bloqueado','Vagas',admin,f'/inscricoes/{second}/confirmar/',n=200,unchanged=True,check={'exige_justificativa':lambda r,b,a:'exige justificativa' in r['text']})
        promote=f'/inscricoes/turmas/{cid}/promover/'
        v.get('Método GET em promoção rejeitado','Autorização',admin,promote,405)
        v.post('Promover manualmente primeiro da fila','Vagas',admin,promote,source=f'/inscricoes/turmas/{cid}/fila/',check={'primeiro_confirmado':lambda r,b,a:v.find(a,'enrollments.Enrollment',id=e2)['status']=='CONFIRMED','segundo_permanece_espera':lambda r,b,a:v.find(a,'enrollments.Enrollment',id=second)['status']=='WAITLISTED','capacidade_preservada':lambda r,b,a:sum(x['status']=='CONFIRMED' and x['class_group_id']==cid for x in a['enrollments.Enrollment'])==1})
        meet={'title':run+' DUPLICATE_BASE','starts_at':(today+timedelta(days=1)).isoformat()+'T08:00','ends_at':(today+timedelta(days=1)).isoformat()+'T09:00'}
        v.post('Preparar encontro para reprodução de duplicidade','Encontros',admin,f'/oficinas/turmas/{cid}/encontros/novo/',meet,check={'um_encontro':lambda r,b,a:len([x for x in a['workshops.Meeting'] if x['class_group_id']==cid])==1})
        v.post('Reproduzir duplicidade de início em turma aberta','Encontros',admin,f'/oficinas/turmas/{cid}/encontros/novo/',meet|{'title':run+' DUPLICATE_REPEAT'},n=200,unchanged=True,check={'erro_amigavel_duplicidade':lambda r,b,a:'já existe' in r['text']})
    # Exercise academic guards via the real, linked Django admin interface as well.
    d={'workshop':workshop,'institution':institution,'code':v.class_code('bypass'),'title':run+' BYPASS','location':run+' sala fictícia','capacity':'1','registration_opens_at':(today-timedelta(days=1)).isoformat()+'T00:00','registration_closes_at':today.isoformat()+'T23:00','start_date':(today+timedelta(days=1)).isoformat(),'end_date':(today+timedelta(days=3)).isoformat(),'waitlist_enabled':'on'}
    v.post('Criar turma exclusiva para testar guardas do admin','Preparação HTTP',admin,'/oficinas/turmas/nova/',d,check={'nova_planejada':lambda r,b,a:v.find(a,'workshops.ClassGroup',code=v.class_code('bypass'))['status']=='PLANNED'})
    cid=v.find(v.snapshot(),'workshops.ClassGroup',code=v.class_code('bypass'))['id'];ap=f'/admin/workshops/classgroup/{cid}/change/'
    page=admin.request(ap);form=next(f for f in v.Forms(page['text']).forms if 'status' in f['names'])
    payload={k:val for k,val in form['fields'].items() if any(k.endswith(x) for x in ['TOTAL_FORMS','INITIAL_FORMS','MIN_NUM_FORMS','MAX_NUM_FORMS'])}
    payload.update(d);payload.update({'status':'COMPLETED','created_by':ids['admin'],'registration_opens_at_0':d['registration_opens_at'].split('T')[0],'registration_opens_at_1':'00:00:00','registration_closes_at_0':d['registration_closes_at'].split('T')[0],'registration_closes_at_1':'23:00:00','_save':'Salvar'})
    v.post('Admin não deve concluir turma sem critérios acadêmicos','Conclusão',admin,ap,payload,n=200,unchanged=True,check={'permanece_planejada':lambda r,b,a:v.find(a,'workshops.ClassGroup',id=cid)['status']=='PLANNED'},expected='Rejeição de formulário; status PLANNED preservado sem instrutor/encontro/avaliação')
    # Full password reset, with token kept only in memory and sanitized endpoint records.
    anon=v.Session('ANONYMOUS_PASSWORD_RESET_FULL');started=datetime.now().astimezone().isoformat()
    v.post('Solicitar redefinição completa em conta fictícia','Recuperação',anon,'/senha/recuperar/',{'email':v.CREDS['p3']['email']},unchanged=True,check={'enviado':lambda r,b,a:r['headers'].get('Location')=='/senha/recuperar/enviado/'})
    raw=subprocess.run(v.COMPOSE+['logs','--no-color','--since',started,'app'],capture_output=True,text=True,timeout=20).stdout
    urls=re.findall(re.escape(v.BASE)+r'(/senha/redefinir/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/)',raw)
    if not urls:raise RuntimeError('Link de recuperação indisponível; nenhum log foi exposto')
    reset=urls[-1]
    r,_=v.get('Validar link de redefinição (token omitido)','Recuperação',anon,reset,302)
    confirm=r['headers']['Location']
    new=secrets.token_urlsafe(30)
    v.post('Redefinir senha somente conta exclusiva','Recuperação',anon,confirm,{'new_password1':new,'new_password2':new},check={'concluido':lambda r,b,a:r['headers'].get('Location')=='/senha/redefinir/concluido/'})
    v.get('Página redefinição concluída','Recuperação',anon,'/senha/redefinir/concluido/')
    v.post('Senha antiga deixou de autenticar','Recuperação',anon,'/entrar/',{'username':v.CREDS['p3']['email'],'password':v.CREDS['p3']['password']},n=200,unchanged=True,check={'login_negado':lambda r,b,a:'E-mail ou senha inválidos' in r['text']})
    v.CREDS['p3']['password']=new
    (a.private_dir/'credentials.json').write_text(json.dumps(v.CREDS));os.chmod(a.private_dir/'credentials.json',0o600)
    v.login('p3',v.CREDS)
    v.get('Token de recuperação não pode ser reutilizado','Recuperação',v.Session('ANONYMOUS_RESET_REUSE'),reset,200,{'link_invalido':lambda r,b,a:'inválido ou já foi utilizado' in r['text'].lower()})
    # Archive/desactivate only entities created here, after academic and report verification.
    v.post('Arquivar oficina exclusiva','Oficinas',admin,f'/oficinas/{workshop}/situacao/archived/',source=f'/oficinas/{workshop}/',check={'arquivada':lambda r,b,a:v.find(a,'workshops.Workshop',id=workshop)['status']=='ARCHIVED'})
    cid=classes['other']
    d={'title':run+' CANCEL_ON_CLASS','starts_at':(today+timedelta(days=1)).isoformat()+'T08:00','ends_at':(today+timedelta(days=1)).isoformat()+'T09:00'}
    v.post('Criar encontro para cancelamento da turma','Encontros',admin,f'/oficinas/turmas/{cid}/encontros/novo/',d,check={'encontro_novo':lambda r,b,a:len(a['workshops.Meeting'])==len(b['workshops.Meeting'])+1})
    v.post('Cancelar turma e encontro futuro','Turmas',admin,f'/oficinas/turmas/{cid}/situacao/cancelled/',source=f'/oficinas/turmas/{cid}/',check={'turma_cancelada':lambda r,b,a:v.find(a,'workshops.ClassGroup',id=cid)['status']=='CANCELLED','encontro_cancelado':lambda r,b,a:v.find(a,'workshops.Meeting',title=run+' CANCEL_ON_CLASS')['status']=='CANCELLED'})
    v.post('Inscrição turma cancelada bloqueada','Inscrições',v.CLIENTS['p3'],f'/inscricoes/turmas/{cid}/solicitar/',source='/',verify=False,unchanged=True,check={'nao_criou':lambda r,b,a:len(a['enrollments.Enrollment'])==len(b['enrollments.Enrollment'])})
    v.get('Agenda turma cancelada não permite criar','Encontros',admin,f'/oficinas/turmas/{cid}/encontros/novo/',403)
    v.post('Arquivar instituição exclusiva','Pessoas',admin,f'/pessoas/instituicoes/{institution}/editar/',{'name':run+' INSTITUTION','address':run+' endereço fictício editado'},check={'instituicao_inativa':lambda r,b,a:not v.find(a,'people.Institution',id=institution)['is_active']})
    v.save()

if __name__=='__main__':
    try:main()
    finally:
        if hasattr(v,'OUT'):
            v.save();s=v.snapshot();(v.OUT/'estado-final-execucao.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));(v.OUT/'ids-execucao.json').write_text(json.dumps({m:[r['id'] for r in rs] for m,rs in s.items()},indent=2));(v.OUT/'dados-existentes-final-hashes.json').write_text(json.dumps(v.existing_hash(),indent=2))
            print('Resumo:',json.dumps({k:sum(c['classification']==k for c in v.CASES) for k in ['APROVADO','REPROVADO','BLOQUEADO','NÃO EXECUTADO']}),flush=True)
