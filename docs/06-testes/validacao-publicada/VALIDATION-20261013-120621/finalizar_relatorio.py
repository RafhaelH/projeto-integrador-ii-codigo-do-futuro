#!/usr/bin/env python3
"""Consolida evidências existentes; somente consultas de leitura e escrita de relatórios."""
import csv
import io
import json
import hashlib
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
import validar as v

v.OUT=Path(__file__).resolve().parent;v.RUN=v.OUT.name
cases=json.loads((v.OUT/'matriz.json').read_text())
(v.OUT/'matriz-antes-revisao-executor.json').write_text(json.dumps(cases,indent=2,ensure_ascii=False))
corrections=[]
def revise(number,expected,observed,checks,refs):
    c=next(c for c in cases if c['id']==number)
    matches=[c for c in cases if c['functionality'] in refs and c['id']!=number and c['classification']=='APROVADO']
    assert matches and all(c['classification']=='APROVADO' for c in matches)
    corrections.append({'id':number,'previous_classification':c['classification'],'previous_checks':c['checks'],'reason':observed,'retests':[c['id'] for c in matches]})
    c.update({'expected':expected,'observed':observed,'checks':checks,'classification':'APROVADO','executor_review':corrections[-1]})

revise('HTTP-161','URL inválida: HTTP 200 com erro; nenhuma alteração de negócio','Resposta 200 e ausência de alterações já comprovadas. Seletor field-error do executor estava errado: este formulário usa errorlist; reteste HTTP confirmou a mensagem de URL inválida.',{'http_formulario':True,'dados_preservados':True},['Reteste URL inválida: mensagem real do formulário'])
revise('HTTP-317','URL inválida: HTTP 200 com mensagem real do formulário e nenhum dado gravado','O seletor do executor esperava Insira, mas a aplicação usa Informe uma URL válida. Requisição real adicional preservou a mensagem sanitizada e confirmou a rejeição sem gravação.',{'http_formulario':True,'dados_preservados':True},['Reteste URL inválida: mensagem real do formulário'])
revise('HTTP-170','Nota 10,1: HTTP 200 com erro; nenhuma alteração de negócio','Resposta 200 e ausência de alterações já comprovadas. Seletor field-error do executor estava errado; reteste HTTP confirmou mensagem de limite 10.',{'http_formulario':True,'dados_preservados':True},['Reteste nota 10,1 com erro visível'])
revise('HTTP-201','Titular não baixa certificado revogado: HTTP 404, sem alteração','HTTP 404 observado: o seletor oculta revogados para titulares. Administrador recebe 403 no download; ambos os comportamentos foram retestados.',{'download_bloqueado':True,'dados_preservados':True},['Reteste download revogado oculto ao titular','Administrador também não baixa PDF revogado'])
revise('HTTP-202','Certificado revogado oculto ao titular; histórico preservado para administrador','HTTP 404 ao titular estava correto. Expectativa inicial de histórico visível ao titular foi corrigida; administrador consultou o histórico real por HTTP 200.',{'oculto_ao_titular':True,'dados_preservados':True},['Reteste consulta revogada oculta ao titular','Histórico revogado preservado para administrador'])
for kind,number in [('inscricoes','HTTP-208'),('frequencia','HTTP-211'),('conclusao','HTTP-214')]:
    initial=json.loads((v.OUT/('csv-'+kind+'-evidencia-primeira-passagem.json')).read_text())
    final=json.loads((v.OUT/('csv-'+kind+'-evidencia.json')).read_text())
    assert initial['sha256']==final['sha256']
    revise(number,'CSV HTTP 200, cabeçalhos e quatro linhas conferidos, filtros e campos protegidos verificados','Contexto do CPF sintético se perdeu na retomada do executor. Repetição HTTP passou todas as verificações; o SHA-256 do CSV é idêntico ao da resposta inicial.',{'http_csv':True,'same_response_sha256_on_retest':True,'csv_validated_by_real_retest':True},['CSV '+kind+' filtros/cabeçalhos/conteúdo'])

limitations=[
 ('Entrega real de e-mail SMTP','E-mail permanece no backend de console autorizado para homologação; não existem credenciais SMTP nesta tarefa.'),
 ('Cinco avaliações humanas e usabilidade','Não há avaliadores nesta execução técnica. As cinco sessões continuam pendentes.'),
 ('Responsividade em desktop e celular','Requisições HTTP não renderizam viewports; inspeção visual ainda necessária.'),
 ('Acessibilidade por teclado, contraste e leitor de tela','Não executada análise visual ou com tecnologia assistiva; HTML servido não comprova acessibilidade.'),
 ('Proteção do único administrador ativo','Não é possível preparar esse estado no banco compartilhado sem desativar contas existentes; a tarefa proíbe essas alterações.'),
]
for i,(name,why) in enumerate(limitations,1):
    cases.append({'id':f'LIMIT-{i:03d}','functionality':name,'group':'Limitações','endpoint':None,'method':None,'profile':None,'preconditions':why,'expected':'Verificação específica em ambiente/pessoas apropriados','observed':why,'status':None,'classification':'NÃO EXECUTADO','timestamp':datetime.now(v.TZ).isoformat(),'evidence':'relatorio.md'})

raw=json.loads(subprocess.check_output(['docker','inspect',*subprocess.check_output(['docker','ps','-aq'],text=True).split()],text=True))
def safe(c):return {'id':c['Id'],'name':c['Name'],'image':c['Image'],'started':c['State']['StartedAt'],'status':c['State']['Status'],'health':c['State'].get('Health',{}).get('Status'),'restarts':c['RestartCount'],'ports':c['NetworkSettings']['Ports'],'project':c['Config'].get('Labels',{}).get('com.docker.compose.project'),'limits':{k:c['HostConfig'].get(k) for k in ['Memory','NanoCpus','PidsLimit']}}
final=[safe(c) for c in raw];initial=json.loads((v.OUT/'containers-inicial.json').read_text());by_name={c['name']:c for c in final}
container_changes=[{'name':c['name'],'before':c,'after':by_name.get(c['name'])} for c in initial if c!=by_name.get(c['name'])]
(v.OUT/'containers-final.json').write_text(json.dumps(final,indent=2));(v.OUT/'containers-comparacao.json').write_text(json.dumps(container_changes,indent=2))
before=json.loads((v.OUT/'dados-existentes-inicial-hashes.json').read_text());after=v.existing_hash()
(v.OUT/'dados-existentes-final-hashes.json').write_text(json.dumps(after,indent=2));data_changes=[k for k in before if before[k]!=after[k]]
(v.OUT/'dados-existentes-comparacao.json').write_text(json.dumps({'unchanged':not data_changes,'changed_models':data_changes},indent=2))
state=v.snapshot();(v.OUT/'estado-final-execucao.json').write_text(json.dumps(state,indent=2,ensure_ascii=False));ids={m:[r['id'] for r in rs] for m,rs in state.items()}
ids['admin.LogEntry']=v.orm("from django.contrib.admin.models import LogEntry\nprint(json.dumps(list(LogEntry.objects.filter(user__full_name__startswith=%r).values_list('pk',flat=True))))" % v.RUN)
(v.OUT/'ids-execucao.json').write_text(json.dumps(ids,indent=2))
(v.OUT/'correcoes-executor.json').write_text(json.dumps(corrections,indent=2,ensure_ascii=False))
for c in cases:c.setdefault('evidence','requisicoes.json#'+','.join(str(x) for x in c.get('requests',[])))
(v.OUT/'matriz.json').write_text(json.dumps(cases,indent=2,ensure_ascii=False))
columns=['id','functionality','endpoint','method','profile','preconditions','expected','observed','status','classification','timestamp','evidence']
with (v.OUT/'matriz.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
    for c in cases:w.writerow({k:json.dumps(c.get(k),ensure_ascii=False) if isinstance(c.get(k),(dict,list)) else c.get(k) for k in columns})

def relevant(text):return [c['id'] for c in cases if text in c['functionality']]
defects=[
 {'id':'DEF-001','severity':'MÉDIO','title':'Início duplicado de encontro retorna HTTP 500','cases':relevant('Encontro início duplicado')+relevant('Reproduzir duplicidade de início'),'steps':['Administrador abre o cadastro de encontro numa turma exclusiva não encerrada.','Envia início e fim válidos, com início igual ao de um encontro existente.'],'expected':'HTTP 200 com erro de duplicidade no formulário; nenhuma gravação.','observed':'HTTP 500 em duas execuções; nenhuma gravação indevida. IntegrityError/UniqueViolation na constraint workshops_meeting_start_unique.','proposal':'Validar (class_group, starts_at) no MeetingForm considerando a instância editada e tratar IntegrityError de disputa como erro de formulário. Manter a constraint.'},
 {'id':'DEF-002','severity':'ALTO','title':'RF-006 sem fluxo para editar o próprio perfil','cases':relevant('RF-006:'),'steps':['Participante autentica pela tela publicada.','Abre a página inicial e procura o ponto de entrada para consultar/editar seu perfil.'],'expected':'Fluxo autenticado para consulta e atualização dos campos próprios permitidos, conforme RF-006 (Must).','observed':'Página HTTP 200 sem opção de edição própria; inventário de URLs não contém endpoint correspondente. Nenhum caminho inexistente foi inventado ou testado.','proposal':'Implementar fluxo próprio por sessão com campos permitidos, objeto vinculado a request.user e proteção contra alteração de papel/permissões; testar os três perfis.'},
 {'id':'DEF-003','severity':'ALTO','title':'Django admin permite concluir turma fora do processamento acadêmico','cases':relevant('Admin não deve concluir turma'),'steps':['Criar turma exclusiva PLANNED, sem instrutor, encontros, inscrições ou avaliações.','Abrir seu formulário real em /admin/workshops/classgroup/<id>/change/.','Enviar status=COMPLETED com os demais campos válidos e management forms das inlines.'],'expected':'Rejeição da alteração e manutenção do estado PLANNED, conforme RN-015/RN-038 e o fluxo de transições.','observed':'Preencher após conferir o caso real.','proposal':'Tornar status somente leitura no ModelAdmin e encaminhar transições ao serviço de domínio; evitar gravações diretas que contornem os critérios. Aplicar guardas equivalentes aos demais modelos acadêmicos expostos no admin.'},
]
admin_case=next(c for c in cases if 'Admin não deve concluir turma' in c['functionality'])
transition=admin_case['persisted_effects']['workshops.ClassGroup'][0]
defects[-1]['observed']=f'HTTP {admin_case["status"]}; status {transition["before"]["status"]} → {transition["after"]["status"]} gravado sem critérios acadêmicos. Apenas a turma exclusiva deste teste foi afetada.'
defects=[d for d in defects if any(c['classification']=='REPROVADO' for c in cases if c['id'] in d['cases'])]
(v.OUT/'defeitos.json').write_text(json.dumps(defects,indent=2,ensure_ascii=False))
lines=['# Defeitos encontrados','']
for d in defects:
    lines+=['## '+d['id']+' — '+d['severity']+' — '+d['title'],'','Casos: '+', '.join(d['cases']), '','Passos:','']+[f'{i}. {step}' for i,step in enumerate(d['steps'],1)]+['','Esperado: '+d['expected'],'','Observado: '+d['observed'],'','Correção proposta: '+d['proposal'],'']
(v.OUT/'defeitos.md').write_text('\n'.join(lines))

counts=Counter(c['classification'] for c in cases);requests=json.loads((v.OUT/'requisicoes.json').read_text());groups=sorted(set(c['group'] for c in cases))
table='| Grupo | APROVADO | REPROVADO | BLOQUEADO | NÃO EXECUTADO |\n|---|---:|---:|---:|---:|\n'
for g in groups:table+='| '+g+' | '+' | '.join(str(sum(c['group']==g and c['classification']==k for c in cases)) for k in ['APROVADO','REPROVADO','BLOQUEADO','NÃO EXECUTADO'])+' |\n'
meta=json.loads((v.OUT/'versao.json').read_text())
report=f'''# Validação funcional publicada — {v.RUN}

**Conclusão: não liberar a aplicação como totalmente validada nem iniciar as cinco avaliações como aceite do MVP enquanto os defeitos altos estiverem abertos.** O fluxo principal foi exercitado por HTTP real, mas RF-006 não possui ponto de entrada e a interface Django admin contorna a guarda de conclusão acadêmica. Também existe HTTP 500 no cadastro de encontro com início duplicado.

Execução: {requests[0]['timestamp']} a {requests[-1]['timestamp']}; timezone America/Sao_Paulo (UTC−03:00). Origem: a própria VPS 31.97.167.150. Todas as chamadas usaram o domínio público e passaram por Nginx/Django com verificação normal de TLS. Não representam uma medição independente a partir de outra rede.

Domínio: {v.BASE}. Diretório: {v.ROOT}. Branch: {meta['git_branch']}; commit: {meta['git_commit']}. Imagem da aplicação: {meta['app_image']}. Containers: codigo-do-futuro-app-1 e codigo-do-futuro-database-1. Aplicação em 127.0.0.1:8031; banco sem porta publicada.

## Resultado quantitativo

{len(cases)} casos registrados, incluindo preparação HTTP, repetições de autenticação e retestes. {len(requests)} requisições reais, timeout de 20 segundos e limite de 650. Execução sequencial, exceto duas confirmações simultâneas na turma exclusiva de última vaga. A matriz JSON contém verificações, efeitos persistidos e hashes do estado; a CSV facilita revisão.

- APROVADO: {counts['APROVADO']}
- REPROVADO: {counts['REPROVADO']}
- BLOQUEADO: {counts['BLOQUEADO']}
- NÃO EXECUTADO: {counts['NÃO EXECUTADO']}

{table}
## Funcionalidades e perfis realmente testados

Administrador isolado, dois instrutores, três participantes adultos e um menor. Sessões independentes por conta; sessão anônima para os bloqueios. Foram testados disponibilidade/TLS/redirecionamento, estáticos, login válido/inválido/inativo, logout, CSRF, permissões por perfil e vínculo, cadastro/pesquisa/edição de pessoas e instituições, responsável do menor, oficinas e estados, turmas/instrutores/cronograma, inscrições e histórico, ocupação/fila/promoção/cancelamento/concorrência, frequência, projetos, avaliações/publicação, conclusão, certificados/PDF/revogação, painel e os três CSVs filtrados.

A turma acadêmica produziu 75%, 50%, 100% e 100% de frequência. O participante com 75%, nota 6,0 e projeto entregue foi aprovado; os outros três não concluíram respectivamente por frequência, nota e ausência de projeto. O certificado teve quatro horas, excluindo encontro cancelado. O painel filtrado indicou uma turma, quatro inscrições, 100% de ocupação, 81,25% de frequência média, três projetos e 25% de aprovação. Os CSVs continham quatro linhas do mesmo universo e não continham CPF, telefone ou e-mail.

Recuperação de senha: formulário, mensagem no console, link com token, redefinição numa conta exclusiva, rejeição da senha anterior, novo login e rejeição de reutilização do token foram exercitados. Tokens permaneceram somente em memória; os caminhos nas evidências usam placeholders. **Isso não comprova entrega SMTP.**

## Preparação e correções do executor

O primeiro administrador isolado foi provisionado por um bootstrap mínimo Django/ORM porque não existe auto provisionamento público sem autenticação administrativa. Isso preservou as contas existentes e não conta como validação HTTP de cadastro. As seis contas seguintes foram criadas pelo endpoint real do Django admin; todos os perfis e registros de negócio foram criados por formulários HTTP. Nenhuma conta [DEMO] foi autenticada, editada ou teve senha alterada. Senhas temporárias ficam exclusivamente em /root/codigo-do-futuro-validation/{v.RUN}/credentials.json, modo 600, diretório 700, fora do Git.

O executor precisou ser retomado após gerar um código de turma maior que 30 caracteres; o servidor corretamente rejeitou a entrada. Os códigos válidos preservam o identificador completo com sufixo curto. Também foram corrigidos seletores de mensagens de formulário, expectativas de certificado revogado e o contexto do CPF após a retomada. As expectativas anteriores estão preservadas em matriz-antes-revisao-executor.json; correcoes-executor.json liga cada revisão a retestes HTTP reais. Para CSV, a resposta inicial e o reteste possuem exatamente o mesmo SHA-256. Nenhuma correção foi aplicada ao código da aplicação.

## Defeitos e pendências

Ver [defeitos.md](defeitos.md) para severidade, passos, resultado esperado/observado e correção proposta. Foram encontrados {len(defects)} defeitos, sem correções nesta tarefa. RF-006 é Must e precisa de implementação e reteste. A guarda acadêmica deve também valer no Django admin. O erro 500 por duplicidade deve ser convertido em erro de formulário.

Os cinco casos LIMIT na matriz explicam testes não executados: SMTP real, cinco avaliações/usabilidade, responsividade, acessibilidade e desativação do único administrador ativo. O último exigiria alterar contas existentes; deve ser testado em banco descartável. Não foi executado teste de carga ou restauração de banco em uso.

## Preservação e dados mantidos

Comparação de containers: {len(container_changes)} diferenças em IDs, início, saúde, reinícios, portas, imagem e limites. Comparação dos dados preexistentes: modelos alterados = {data_changes}. As duas imagens/containers do projeto continuam saudáveis. Nenhum deploy, nova migração, alteração de código da aplicação, push, merge, promoção de branch ou alteração de infraestrutura foi realizado. Os únicos arquivos locais novos estão nesta pasta de evidências.

hospitalar-staging-docs e bancodetalentos_frontend já estavam unhealthy e permaneceram assim; hospitalar-staging-migrate também já estava parado/unhealthy. Nenhum serviço de outro projeto foi reiniciado ou corrigido.

Os dados fictícios desta execução foram mantidos, incluindo o certificado revogado e a turma usada para demonstrar a guarda ausente. Todos são identificáveis por {v.RUN}. O plano abaixo não foi executado.

## Plano de remoção restrita

1. Criar backup e revisar [ids-execucao.json](ids-execucao.json); confirmar cada ID e seus vínculos antes de qualquer alteração. Usar somente esses IDs, nunca filtros globais ou exclusão por um prefixo genérico.
2. Preferir desativar as sete contas e perfis desta execução e cancelar/arquivar as turmas/oficina exclusivas, preservando histórico. O certificado revogado já mantém seu registro histórico.
3. Se houver autorização posterior para remoção física, avaliar transação e dependências: logs do admin desta execução, frequências, avaliações, projetos, histórico de inscrições, certificado, inscrições, encontros, vínculos de instrutores e responsáveis, turmas, oficina, perfis, responsáveis/instituição e usuários. Respeitar PROTECT e a proibição de delete de certificado; não contornar essas guardas automaticamente.
4. Invalidar somente sessões cujos usuários decodificados correspondam aos IDs desta execução. Não listar ou gravar chaves de sessão no relatório. Excluir depois o arquivo privado de credenciais, conforme retenção acordada.
5. Conferir contagens/IDs e hashes dos dados existentes após a operação e repetir o smoke test. Nenhuma etapa destrutiva desse plano foi executada nesta tarefa.

## Reprodução e artefatos

- validar.py: executor principal; nova execução usa novo identificador e novo diretório privado.
- complementar.py: executado após o principal, com o mesmo identificador e diretório privado.
- reteste_formulario.py: reteste pontual que preservou somente a mensagem de erro sanitizada.
- finalizar_relatorio.py: consolidação desta execução, com consultas de leitura; revisões históricas referenciam seus IDs originais.
- matriz.json / matriz.csv: casos e classificação final.
- requisicoes.json: trilha sanitizada de requisições, sem corpos completos, cookies ou tokens.
- estado-final-execucao.json / ids-execucao.json: registros exclusivos e seus efeitos.
- endpoints-descobertos.json: inventário real de URLs da aplicação.
- pdf-evidencia.json e csv-*-evidencia.json: fingerprints e verificações dos documentos.
- diagnostico-sanitizado.json: somente tipos de exceção e nome da constraint.
- containers-*.json / dados-existentes-*.json: preservação do ambiente e dos cenários existentes.

```bash
cd {v.ROOT}
PYTHONDONTWRITEBYTECODE=1 python3 {v.OUT.relative_to(v.ROOT)}/validar.py --private-dir /root/codigo-do-futuro-validation/NOVA-EXECUCAO
# Use o identificador impresso/gerado na pasta e o mesmo diretório privado:
PYTHONDONTWRITEBYTECODE=1 python3 {v.OUT.relative_to(v.ROOT)}/complementar.py --private-dir /root/codigo-do-futuro-validation/NOVA-EXECUCAO --run-id VALIDATION-AAAAMMDD-HHMMSS
```

A validação técnica não substitui as cinco avaliações reais e não comprova, sozinha, usabilidade, responsividade ou acessibilidade.
'''
(v.OUT/'relatorio.md').write_text(report)
summary={'classifications':dict(counts),'cases':len(cases),'requests':len(requests),'defects':defects,'container_changes':container_changes,'existing_data_changed_models':data_changes,'ready_for_human_acceptance':False}
(v.OUT/'resumo.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps({'cases':len(cases),'requests':len(requests),'counts':dict(counts),'defects':[{k:d[k] for k in ['id','severity','title']} for d in defects],'container_changes':len(container_changes),'data_changes':data_changes},indent=2,ensure_ascii=False))
