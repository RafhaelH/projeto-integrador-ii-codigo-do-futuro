# Escopo do MVP

## Incluído

### Acesso e pessoas

- autenticação por e-mail e senha;
- recuperação de senha;
- ativação e desativação de usuários;
- perfis de administrador, instrutor e participante;
- cadastro de participantes, responsáveis e instrutores;
- vínculo de participante menor de idade com responsável;
- cadastro de instituições parceiras.

### Oferta educacional

- cadastro e publicação de oficinas;
- criação de turmas com período, local, capacidade e instrutores;
- abertura e encerramento de inscrições;
- planejamento dos encontros de cada turma.

### Jornada do participante

- inscrição em turma;
- análise ou confirmação de inscrição;
- controle automático de vagas;
- lista de espera ordenada;
- cancelamento e promoção da lista de espera;
- consulta ao cronograma;
- registro de frequência;
- submissão ou registro de projeto individual;
- avaliação final;
- definição de conclusão;
- emissão e consulta de certificado.

### Gestão e acompanhamento

- painel com indicadores essenciais;
- relatórios de ocupação, frequência e conclusão;
- filtros por oficina, turma, período e situação;
- trilha mínima de autoria e datas de criação/alteração.

## Fora do escopo do MVP

- pagamentos, cobranças ou mensalidades;
- aulas ao vivo, videoconferência ou hospedagem de vídeos;
- chat interno;
- aplicativo móvel nativo;
- integração automática com escolas, bibliotecas ou sistemas governamentais;
- integração com redes sociais;
- gamificação, ranking e pontuação;
- turmas totalmente on-line;
- projetos em grupo;
- assinatura digital ou validação pública externa de certificados;
- acesso autenticado específico para responsáveis;
- envio de SMS ou WhatsApp;
- relatórios analíticos avançados ou inteligência artificial.

## Fronteiras dos conceitos

- **Oficina** descreve a oferta pedagógica reutilizável, como “Introdução à Programação”.
- **Turma** é uma realização concreta de uma oficina, com datas, vagas, local e instrutores.
- **Encontro** é uma aula ou atividade agendada dentro da turma.
- **Inscrição** liga um participante a uma turma e registra sua situação.
- **Projeto** é a entrega individual produzida pelo participante naquela turma.

## Priorização MoSCoW

| Prioridade | Conteúdo |
|---|---|
| Must | autenticação, pessoas, oficinas, turmas, encontros, inscrições, vagas, frequência, avaliação, conclusão e painel básico |
| Should | lista de espera, projetos, certificados e relatórios exportáveis |
| Could | notificações por e-mail e importação de participantes |
| Won't now | todos os itens explicitamente fora do escopo |

## Critério para mudança de escopo

Uma nova funcionalidade só entra no MVP quando:

1. resolve uma necessidade diretamente ligada ao objetivo geral;
2. não compromete a conclusão dos itens Must;
3. possui requisito, regra e critério de aceite documentados;
4. pode ser testada antes da avaliação com os cinco usuários.

## Escopo final verificado em 13/10/2026

O MVP descrito foi implementado na candidata a351c5a/develop 644e7a6, com consultas e comandos nos sete módulos. Perfis próprios editam somente nome/e-mail. Certificado é consultado por código em documento autenticado, sem verificação pública externa; revogação não permite reemissão. Responsáveis não recebem login. Recuperação existe, mas a publicação usa console e não entrega SMTP externo. A lista de ofertas não possui busca textual; filtros do painel usam oficina/status e período de início da turma.

Os campos derivados não são editados para a apresentação: serviços calculam frequência/conclusão, e as capturas registram os valores reais dos dados fictícios. A [rastreabilidade](../02-requisitos/rastreabilidade-implementada.md) explicita lacunas RNF e não afirma que todas as metas de qualidade já foram comprovadas.

## Evolução comprovada e limitação histórica

| Marco Git | Evolução documentável |
|---|---|
| 5730e37 (11/09/2026) | Fundação documental de Integrador II: visão, escopo, requisitos, modelagem e planejamento |
| d081693 a 0ff0bba | Fundação executável, pessoas, ofertas e inscrições |
| cba6b91 a b4e1408 (14/09/2026) | Frequência, projetos/avaliação/conclusão, certificados e reporting |
| d883272 / 00665be | Carga fictícia e candidata de produção |
| cccfa6e / PR #11 / 8924a6d | Perfil próprio RF-006, erro de encontro duplicado e guardas acadêmicas no admin; retestes |
| 3be6200 / a351c5a / PR #12 / 644e7a6 | Dados comprovadamente fictícios, espaços humanos, manual/capturas/PDFs, cronologia e 235 testes |
| Revisão documental atual | Modelo implementado, conformidade do PDF e pendências humanas/AVA; sem nova funcionalidade/deploy |

Esses marcos vêm do histórico versionado, não de reuniões ou depoimentos. Não foi encontrado o planejamento/protótipo original do Integrador I; a origem extensionista descrita na visão é contexto declarado, não prova de revisão acadêmica I. O estudante deve anexar o original e explicitar alterações, ou explicar essa limitação ao tutor.
