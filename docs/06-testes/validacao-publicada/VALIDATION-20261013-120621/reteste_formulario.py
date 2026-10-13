#!/usr/bin/env python3
"""Reteste pontual sem mudar a aplicação; usa apenas a conta exclusiva e entrada inválida."""
import argparse,json,re,html
from pathlib import Path
import validar as v

p=argparse.ArgumentParser();p.add_argument('--private-dir',required=True,type=Path);p.add_argument('--run-id',required=True);args=p.parse_args()
v.RUN=args.run_id;v.PRIVATE=args.private_dir;v.OUT=v.ROOT/'docs/06-testes/validacao-publicada'/v.RUN
v.CASES=json.loads((v.OUT/'matriz.json').read_text());v.REQUESTS=json.loads((v.OUT/'requisicoes.json').read_text());creds=json.loads((args.private_dir/'credentials.json').read_text())
c=v.login('p1',creds);s=v.snapshot();user=v.find(s,'accounts.User',full_name=v.RUN+' P1')['id'];participant=v.find(s,'people.Participant',user_id=user)['id'];cid=v.find(s,'workshops.ClassGroup',code=v.class_code('started'))['id'];eid=v.find(s,'enrollments.Enrollment',class_group_id=cid,participant_id=participant)['id']
def errors(text):
    tags=re.findall(r'<ul[^>]*class="errorlist"[^>]*>.*?</ul>',text,re.S)
    return [html.unescape(re.sub(r'<[^>]+>','',t)).strip() for t in tags]
r,_=v.post('Reteste URL inválida: mensagem real do formulário','Projetos',c,f'/acompanhamento/inscricoes/{eid}/projeto/',{'title':v.RUN+' INVALID_URL_RETEST','description':v.RUN+' fictício','repository_url':'not a url','is_delivered':'on'},n=200,unchanged=True,check={'erro_url_visivel':lambda r,b,a:any('url' in e.lower() and 'válid' in e.lower() for e in errors(r['text']))})
observed=errors(r['text']);assert all('@' not in e and not re.search(r'\d{11}',e) for e in observed)
(v.OUT/'mensagens-formulario-sanitizadas.json').write_text(json.dumps({'case_id':v.CASES[-1]['id'],'errors':observed},ensure_ascii=False,indent=2));v.save();print('Mensagens de erro:',json.dumps(observed,ensure_ascii=False))
