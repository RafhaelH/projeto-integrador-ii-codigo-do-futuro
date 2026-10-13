# Relatório final — base de consolidação

> Este documento está estruturado antes da publicação. Campos marcados como **PENDENTE** dependem
> da VPS, das cinco avaliações ou da tag final e não devem ser preenchidos com dados simulados.

## 1. Identificação

- Projeto: **Código do Futuro**
- Disciplina: **Projeto Integrador Transdisciplinar em Engenharia de Software II**
- Autor: **Rafhael Henrique**
- Curso: **Engenharia de Software**
- Repositório: <https://github.com/RafhaelH/projeto-integrador-ii-codigo-do-futuro>
- URL publicada: **PENDENTE**
- Tag/SHA final: **PENDENTE**
- Data de conclusão: **PENDENTE**

## 2. Problema e justificativa

A realização de oficinas gratuitas de programação envolve cadastros, turmas, vagas, encontros,
frequência, projetos, avaliações e certificados. Quando esses dados ficam dispersos em planilhas
e mensagens, torna-se difícil garantir consistência, rastreabilidade e acompanhamento individual.
O Código do Futuro centraliza essa jornada para jovens de 14 a 21 anos, instrutores e equipe
administrativa.

## 3. Objetivo

Construir uma aplicação web capaz de organizar a oferta das oficinas e acompanhar o participante
da inscrição à conclusão, aplicando regras explícitas de elegibilidade, capacidade, frequência,
avaliação, autorização e emissão de certificado.

## 4. Solução entregue

A aplicação inclui autenticação por perfil; pessoas e instituições; oficinas, turmas e encontros;
inscrições e lista de espera; frequência; projetos; avaliação e conclusão; certificados em PDF;
painéis e relatórios CSV; além de uma carga determinística com dados fictícios.

## 5. Arquitetura e tecnologias

O sistema adota monólito modular renderizado no servidor, usando Python 3.12, Django 5.2 LTS,
PostgreSQL 17, HTML, CSS, JavaScript, Pytest, Ruff, uv e GitHub Actions. A publicação usa Docker,
Gunicorn, Nginx e HTTPS. As regras transacionais permanecem em serviços de domínio, e consultas
gerenciais de leitura ficam no módulo `reporting`.

## 6. Verificação técnica

- Suíte local final: **PENDENTE**
- Cobertura final: **PENDENTE**
- Execução CI/PostgreSQL final: **PENDENTE**
- Migrações em banco vazio: **PENDENTE**
- `check --deploy`: **PENDENTE**
- Smoke test público: **PENDENTE**
- Backup e restauração testados: **PENDENTE**

As evidências devem apontar para o documento de testes e para a execução da tag final.

## 7. Validação com cinco pessoas

| Avaliação | Perfil | Data | Versão | Resultado geral |
|---|---|---|---|---|
| 01 | Participante | PENDENTE | PENDENTE | PENDENTE |
| 02 | Participante | PENDENTE | PENDENTE | PENDENTE |
| 03 | Instrutor | PENDENTE | PENDENTE | PENDENTE |
| 04 | Instrutor | PENDENTE | PENDENTE | PENDENTE |
| 05 | Administrador | PENDENTE | PENDENTE | PENDENTE |

Descrever método, tarefas, taxa de conclusão, notas, problemas e limitações sem omitir falhas.

## 8. Melhorias e decisões

Resumir o `registro-de-melhorias.md`, relacionando cada achado com decisão, justificativa,
PR/commit e reteste. Separar correções implementadas, melhorias futuras, recusas justificadas e
duplicidades.

## 9. Resultado e limitações

Comparar os critérios de aceite com a versão final, informar itens fora do MVP e registrar riscos
remanescentes. Nenhum erro crítico ou alto pode permanecer aberto na entrega.

## 10. Conclusão

Consolidar como o projeto percorreu planejamento, desenvolvimento, verificação automatizada,
validação por pares e melhoria contínua. Registrar a versão exata que corresponde ao código,
manual, PDF e vídeo.

## 11. Anexos

- manual do usuário com screenshots;
- PDF das cinco avaliações;
- registro consolidado de melhorias;
- evidências de testes e CI;
- diagramas e dicionário de dados;
- link do vídeo narrado.
