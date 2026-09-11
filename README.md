# Código do Futuro

Projeto acadêmico desenvolvido para o **Projeto Integrador Transdisciplinar em Engenharia de Software II**.

A plataforma Código do Futuro apoiará a organização de oficinas gratuitas de programação e tecnologia, permitindo acompanhar participantes, responsáveis, instrutores, turmas, inscrições, encontros, frequência, projetos, avaliações, certificados e indicadores de resultado.

## Situação do projeto

A especificação e a fundação executável estão concluídas. O repositório já possui projeto Django, usuário customizado, configurações por ambiente, PostgreSQL local, autenticação, recuperação de senha, interface-base responsiva, testes automatizados e integração contínua.

## Objetivo

Centralizar a gestão das oficinas e substituir controles dispersos por um fluxo único, confiável e acessível, permitindo que administradores e instrutores acompanhem a jornada de cada participante e que os jovens consultem sua própria evolução.

## Escopo do MVP

- autenticação e recuperação de acesso;
- gerenciamento de usuários e perfis;
- participantes e responsáveis;
- instrutores e instituições parceiras;
- oficinas, turmas e encontros;
- inscrições, vagas e lista de espera;
- registro e consulta de frequência;
- projetos e avaliações dos participantes;
- conclusão e emissão de certificados;
- painel gerencial e relatórios básicos.

## Stack

- Python 3.12 e Django 5.2 LTS;
- PostgreSQL 17;
- templates Django, HTML, CSS e JavaScript;
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
uv run python src/manage.py runserver
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
uv sync
docker compose up -d database
uv run python src/manage.py migrate
uv run python src/manage.py createsuperuser
uv run python src/manage.py runserver
```

A aplicação ficará disponível em `http://127.0.0.1:8000/` e a área administrativa em `http://127.0.0.1:8000/admin/`.

## Verificações

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
DJANGO_SETTINGS_MODULE=config.settings.test uv run python src/manage.py check
DJANGO_SETTINGS_MODULE=config.settings.test uv run python src/manage.py makemigrations --check --dry-run
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
│   └── people/      # participantes, responsáveis, instrutores e instituições
├── config/
│   └── settings/    # base, local, test e production
├── static/          # estilos e recursos públicos
├── templates/       # templates globais e autenticação
└── manage.py
```

Os módulos `workshops`, `enrollments`, `learning` e `reporting` serão adicionados incrementalmente conforme o backlog.

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
- [Backlog](docs/05-planejamento/backlog.md)
- [Plano de testes](docs/06-testes/plano-de-testes.md)
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
