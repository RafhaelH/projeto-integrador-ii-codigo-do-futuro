# Roteiro do vídeo final — cinco minutos

O documento da disciplina contém as expressões “até cinco minutos” e “pelo menos cinco minutos”.
Para atender às duas orientações, a gravação deve terminar em **5:00**, com tolerância apenas da
plataforma de vídeo. A narração deve ser feita pelo autor e usar a mesma tag da entrega.

## Preparação

- fechar notificações e abas pessoais;
- usar dados exclusivamente fictícios;
- ampliar o cursor e definir zoom legível;
- deixar abertas as contas necessárias em perfis separados do navegador;
- confirmar domínio, HTTPS, tag/SHA e smoke test;
- ensaiar com cronômetro antes da gravação final.

## Cronograma e fala-base

### 0:00–0:30 — Problema e público

“Este é o Código do Futuro, desenvolvido no Projeto Integrador Transdisciplinar em Engenharia de
Software II. A plataforma substitui controles dispersos na gestão de oficinas gratuitas de
programação para jovens de 14 a 21 anos, centralizando pessoas, turmas e acompanhamento.”

Mostrar a tela de entrada e a identidade da solução.

### 0:30–1:00 — Objetivo e perfis

“O sistema possui três perfis. O administrador organiza a oferta e acompanha indicadores; o
instrutor registra a jornada pedagógica somente das turmas vinculadas; e o participante consulta
inscrições, frequência, projeto, avaliação e certificado.”

Mostrar rapidamente a navegação de cada perfil.

### 1:00–2:00 — Administração da oficina

No perfil administrador:

1. abrir Pessoas e mostrar participante com responsável;
2. abrir uma oficina publicada;
3. abrir turma com capacidade, instrutores e encontros;
4. mostrar inscrição pendente e lista de espera.

Fala-chave: “As regras impedem duplicidade, validam menores com responsável e protegem a última
vaga com transação no banco.”

### 2:00–3:00 — Jornada pedagógica

No perfil instrutor:

1. mostrar somente as turmas vinculadas;
2. abrir o acompanhamento;
3. mostrar chamada por encontro;
4. mostrar projeto, avaliação e critérios de conclusão.

Fala-chave: “A aprovação exige 75% de frequência, nota mínima 6,0 e projeto entregue. As
alterações registram autoria e preservam o histórico.”

### 3:00–3:35 — Experiência do participante

No perfil participante:

1. abrir Minha jornada;
2. mostrar frequência, devolutiva e resultado;
3. abrir certificado e iniciar o download do PDF.

### 3:35–4:05 — Painel, relatórios e arquitetura

No administrador, mostrar o painel filtrado e os três CSVs. Explicar em uma frase:

“A solução é um monólito modular em Django 5.2 e Python 3.12, com PostgreSQL 17, Gunicorn, Nginx,
Docker e HTTPS. A separação em módulos mantém as regras testáveis sem aumentar a operação.”

### 4:05–4:30 — Verificação e validação

Mostrar a página do repositório/CI e uma evidência consolidada:

“A versão final possui testes automatizados de modelos, serviços, permissões, interface,
concorrência e relatórios, executados em PostgreSQL na integração contínua. Também foi avaliada
por cinco pessoas nas perspectivas de participante, instrutor e administrador.”

Substituir pela contagem e cobertura exatas da tag final.

### 4:30–4:50 — Melhorias das avaliações

Apresentar de duas a três mudanças reais, sempre com origem e resultado:

“As avaliações identificaram [ACHADO]. A decisão foi [DECISÃO], implementada em [ALTERAÇÃO]. O
reteste confirmou [RESULTADO]. Sugestões fora do MVP foram justificadas no relatório.”

Não inventar melhorias antes das avaliações.

### 4:50–5:00 — Encerramento

“O Código do Futuro entrega uma gestão rastreável das oficinas e evidencia um ciclo completo de
planejamento, implementação, testes, validação e melhoria contínua. Repositório, manual e PDF das
avaliações acompanham a entrega.”

## Checklist da gravação

- [ ] Autor narrou o vídeo.
- [ ] Duração final conferida em 5:00.
- [ ] Problema, público e objetivo apresentados.
- [ ] Front-end e back-end em funcionamento demonstrados.
- [ ] Arquitetura e tecnologias explicadas.
- [ ] Testes automatizados e cinco avaliações mencionados.
- [ ] Melhorias reais apresentadas.
- [ ] Nenhum dado pessoal ou segredo exposto.
- [ ] Aplicação, manual, PDF e vídeo usam a mesma tag.
