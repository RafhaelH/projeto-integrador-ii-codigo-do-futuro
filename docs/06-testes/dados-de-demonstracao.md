# Dados de demonstração

## Ambiente publicado preparado em 13/10/2026

A VPS usa agora **prepare_presentation**, com origem e IDs comprovados, nomes naturais, contas individuais aleatórias e espaços A01–A05. Consulte o [relatório e operação](preparacao-20261013/relatorio.md) e o [pacote de avaliação](../07-avaliacoes/pacote-de-avaliacao.md). A senha operacional foi preservada; nenhuma senha do ambiente publicado está neste documento. O comando antigo seed_demo fica bloqueado quando identifica a apresentação preparada, para evitar recriar os e-mails e nomes antigos.

As seções abaixo descrevem somente a carga antiga para desenvolvimento descartável, antes da preparação. Não as execute para renovar o ambiente publicado.

## Objetivo

A carga determinística prepara uma base exclusivamente fictícia para apresentação, testes
manuais e avaliação com usuários. Ela não apaga registros e pode ser executada novamente:
os mesmos registros reservados são atualizados sem duplicação.

## Execução local

Após aplicar as migrações:

```bash
uv run python src/manage.py seed_demo
```

Todos os e-mails usam o domínio reservado `demo.codigodofuturo.local`, os nomes visíveis
começam com `[DEMO]` e os códigos das turmas começam com `DEMO-`.

## Credenciais

| Perfil | E-mail | Senha local |
|---|---|---|
| Administrador | `admin@demo.codigodofuturo.local` | senha local do seed, apenas desenvolvimento |
| Instrutora | `larissa.instrutora@demo.codigodofuturo.local` | senha local do seed, apenas desenvolvimento |
| Instrutor | `rafael.instrutor@demo.codigodofuturo.local` | senha local do seed, apenas desenvolvimento |
| Participante | `ana.oliveira@demo.codigodofuturo.local` | senha local do seed, apenas desenvolvimento |

Os outros participantes usam o mesmo domínio e a mesma senha local. Nunca reutilize essa
senha fora de um ambiente descartável de desenvolvimento ou homologação.

## Conteúdo criado

| Entidade | Quantidade |
|---|---:|
| Usuários | 9 |
| Participantes | 6 |
| Instrutores | 2 |
| Responsáveis e vínculos | 3 |
| Instituições | 1 |
| Oficinas | 3 |
| Turmas | 4 |
| Encontros | 10 |
| Inscrições | 9 |
| Registros de frequência | 12 |
| Projetos | 4 |
| Avaliações | 3 |
| Certificados | 1 |

## Cenários disponíveis

- turma de Python concluída, com uma aprovação certificada e uma não conclusão por frequência;
- turma de desenvolvimento web em andamento, com presença, falta, projeto entregue e rascunho;
- turma de robótica aberta e lotada, com duas confirmações, espera e solicitação pendente;
- próxima turma planejada, ainda sem inscrições;
- participantes adultos e menores com responsáveis ativos;
- inscrições pendente, confirmada, em espera, cancelada, aprovada e não concluída.

## Segurança

Com `DEBUG=False`, o comando é bloqueado por padrão. Em uma homologação isolada, a liberação
exige simultaneamente uma senha definida no ambiente e a opção explícita:

```bash
DEMO_PASSWORD='troque-esta-senha' uv run python src/manage.py seed_demo --allow-production
```

Não execute a carga no banco que contenha dados pessoais reais. O comando não faz limpeza
global e não altera superusuários existentes; ele atua somente nas identidades reservadas.
