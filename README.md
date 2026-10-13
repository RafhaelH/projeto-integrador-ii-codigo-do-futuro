# Código do Futuro

Projeto acadêmico desenvolvido para o **Projeto Integrador Transdisciplinar em Engenharia de Software II**.

A plataforma Código do Futuro apoia a organização de oficinas gratuitas de programação e tecnologia, permitindo acompanhar participantes, responsáveis, instrutores, turmas, inscrições, encontros, frequência, projetos, avaliações, certificados e indicadores de resultado.

## Situação do projeto

A especificação, a fundação executável e os módulos operacionais do MVP estão concluídos. O sistema já permite autenticação, recuperação de senha, gestão de participantes, responsáveis, instrutores, instituições, oficinas, turmas, encontros, inscrições, vagas, lista de espera, frequência, projetos, avaliações e processamento objetivo do resultado, certificados em PDF, painéis por perfil e relatórios CSV protegidos, com testes automatizados e integração contínua. A release candidata também possui empacotamento Docker, configuração de produção, health checks, backup e material para as cinco avaliações exigidas pela disciplina.

## Estado acadêmico verificado

Em 13/10/2026, develop está em `644e7a6` e código publicado em `a351c5a` (mesmo src), com 235 testes em PostgreSQL isolado e cobertura 89,84%. Manual ilustrado, 38 imagens e modelos estão preparados; **cinco avaliações humanas e vídeo narrado continuam pendentes**. O [índice para o tutor](docs/09-entrega/README.md), a [matriz](docs/09-entrega/matriz-conformidade.md) e o [checklist](docs/09-entrega/checklist-final.md) distinguem evidências e lacunas. A revisão do planejamento original I e o modelo específico AVA ainda precisam ser conferidos pelo estudante. Main permanece preservada.

## Objetivo

Centralizar a gestão das oficinas e substituir controles dispersos por um fluxo único, com regras verificáveis, permitindo que administradores e instrutores acompanhem a jornada de cada participante e que os jovens consultem sua própria evolução.

## Escopo do MVP

- autenticação e recuperação de acesso;
- gerenciamento de usuários e perfis;
- participantes e responsáveis;
- instrutores e instituições parceiras;
- oficinas, turmas e encontros;
- inscrições, vagas e lista de espera;
- registro e consulta de frequência;
- projetos e avaliações dos participantes;
- certificados autenticados e revogáveis;
- painel gerencial e relatórios básicos.

## Stack

- Python 3.12 e Django 5.2 LTS;
- PostgreSQL 17;
- templates Django, HTML e CSS;
- Pytest para testes automatizados;
- Ruff para lint e formatação;
- uv para dependências reproduzíveis;
- GitHub Actions para integração contínua.

As versões exatas resolvidas estão registradas em `uv.lock`.

## Executar localmente

### Pré-requisitos

- Python 3.12;
- [uv](https://docs.astral.sh/uv/);
- Docker com Compose para o PostgreSQL.

### Linux/macOS

```bash
cp .env.example .env
uv sync
docker compose up -d database
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py seed_demo
uv run python src/manage.py runserver
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
uv sync
docker compose up -d database
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py seed_demo
uv run python src/manage.py runserver
```

A aplicação ficará disponível em `http://127.0.0.1:8000/` e a área administrativa em `http://127.0.0.1:8000/admin/`.

O comando `seed_demo` é opcional e cria somente dados fictícios reservados para apresentação. Consulte [Dados de demonstração](docs/06-testes/dados-de-demonstracao.md) para cenários e cuidados de execução. A candidata publicada usa preparação própria e credenciais restritas fora do Git.

## Publicar na VPS

A implantação acadêmica usa Docker Compose, PostgreSQL 17, Gunicorn e o Nginx da VPS com HTTPS.
O fluxo resumido é:

```bash
cp deploy/production.env.example deploy/production.env
chmod 600 deploy/production.env
# Substitua todos os valores de exemplo antes de continuar.
./deploy/check-env.sh deploy/production.env
./deploy/deploy.sh deploy/production.env
```

Não versione `deploy/production.env`. DNS, Certbot, Nginx, carga demonstrativa, backup,
restauração e atualização estão detalhados no [guia de implantação](docs/04-arquitetura/implantacao-vps.md).

## Verificações

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
DJANGO_SETTINGS_MODULE=config.settings.test uv run python src/manage.py check
DJANGO_SETTINGS_MODULE=config.settings.test uv run python src/manage.py makemigrations --check --dry-run
sh -n deploy/*.sh
```

O limite mínimo inicial de cobertura é 80%. Regras críticas devem possuir cobertura direta independentemente da porcentagem global.

## Configurações

| Ambiente | Módulo | Finalidade |
|---|---|---|
| Desenvolvimento | `config.settings.local` | debug, e-mail no console e banco configurado no `.env` |
| Testes | `config.settings.test` | execução isolada e determinística |
| Produção | `config.settings.production` | HTTPS, cookies seguros, HSTS e variáveis obrigatórias |

Nunca versione `.env`, credenciais, backups ou dados pessoais reais.

## Estrutura do código

```text
src/
├── apps/
│   ├── accounts/    # usuário customizado, autenticação e autorização
│   ├── core/        # páginas compartilhadas e health check
│   ├── enrollments/ # inscrições, vagas, fila e histórico de transições
│   ├── learning/    # frequência e evolução da jornada acadêmica
│   ├── people/      # participantes, responsáveis, instrutores e instituições
│   ├── reporting/   # indicadores, filtros e relatórios CSV
│   └── workshops/   # oficinas, turmas, instrutores vinculados e encontros
├── config/
│   └── settings/    # base, local, test e production
├── static/          # estilos e recursos públicos
├── templates/       # templates globais e autenticação
└── manage.py
```

Os certificados integram o módulo `learning`; indicadores e exportações ficam isolados no
módulo `reporting`, que consulta os demais domínios sem alterar seus registros.

## Documentação

O índice completo está em [`docs/README.md`](docs/README.md).

Documentos centrais:

- [Visão do produto](docs/01-contexto/visao-do-produto.md)
- [Escopo](docs/01-contexto/escopo.md)
- [Requisitos funcionais](docs/02-requisitos/requisitos-funcionais.md)
- [Requisitos não funcionais](docs/02-requisitos/requisitos-nao-funcionais.md)
- [Regras de negócio](docs/02-requisitos/regras-de-negocio.md)
- [Matriz de permissões](docs/02-requisitos/matriz-permissoes.md)
- [Critérios de aceite e rastreabilidade](docs/02-requisitos/criterios-de-aceite.md)
- [Casos de uso](docs/03-modelagem/casos-de-uso.md)
- [Modelo de dados](docs/03-modelagem/modelo-de-dados.md)
- [Arquitetura](docs/04-arquitetura/arquitetura.md)
- [Implantação na VPS](docs/04-arquitetura/implantacao-vps.md)
- [Backlog](docs/05-planejamento/backlog.md)
- [Plano de testes](docs/06-testes/plano-de-testes.md)
- [Pacote das cinco avaliações](docs/07-avaliacoes/pacote-de-avaliacao.md)
- [Manual do usuário](docs/08-manual/README.md)
- [Plano de fechamento](docs/09-entrega/plano-de-fechamento.md)
- [Checklist acadêmico](docs/09-entrega/checklist.md)

## Estratégia de branches

- `main`: versões estáveis e entregáveis;
- `develop`: integração do trabalho em andamento;
- `feat/<descricao>`: funcionalidades;
- `fix/<descricao>`: correções;
- `docs/<descricao>`: documentação.

Cada branch deve sair de `develop` e retornar por pull request após lint, testes e revisão das migrações.

## Origem acadêmica

O sistema evolui o projeto de extensão **Código do Futuro: Oficina de Programação e Tecnologia para Jovens**, realizado em Santa Rosa de Viterbo/SP com jovens de 14 a 21 anos. A experiência prática da oficina é utilizada como base para definir o problema, as funcionalidades e os critérios de acompanhamento da plataforma.

## Autor

Rafhael Henrique — Engenharia de Software.

Repositório: <https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro>
