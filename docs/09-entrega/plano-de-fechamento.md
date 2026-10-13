# Plano de fechamento da entrega

O produto está na transição entre a fase 6 (release candidata) e a fase 7 (validação). O
fechamento é dividido em gates para garantir que código, evidências, manual, PDF e vídeo
representem a mesma versão.

## Gate A — Preparação antes da VPS

- [x] MVP funcional implementado.
- [x] Carga determinística criada.
- [x] Infraestrutura Docker de produção preparada.
- [x] Configuração Nginx e HTTPS documentada.
- [x] Health check e readiness check disponíveis.
- [x] Backup e restauração documentados e automatizados.
- [x] Manual textual concluído.
- [x] Plano de screenshots definido.
- [x] Pacote e cinco formulários de avaliação preparados.
- [x] Relatório acadêmico estruturado.
- [x] Roteiro de vídeo cronometrado.
- [ ] Branch aprovada na CI e integrada à `develop`.

## Gate B — Publicação da release candidata

- [ ] DNS apontando para a VPS.
- [ ] `deploy/production.env` criado somente no servidor.
- [ ] Aplicação e PostgreSQL saudáveis.
- [ ] HTTPS válido e renovação testada.
- [ ] Carga demo executada na homologação isolada.
- [ ] Smoke test externo aprovado.
- [ ] Backup inicial criado e copiado para fora da VPS.
- [ ] URL e SHA registrados.

## Gate C — Cinco avaliações

- [ ] Cinco pessoas confirmadas.
- [ ] Duas avaliações na perspectiva de participante.
- [ ] Duas avaliações na perspectiva de instrutor.
- [ ] Uma avaliação na perspectiva administrativa.
- [ ] Nome/identificação, data, versão e ambiente registrados.
- [ ] Funcionalidades aprovadas, reprovadas e não testadas registradas.
- [ ] Screenshots autorizadas e anonimizadas organizadas.
- [ ] Achados consolidados e classificados.

## Gate D — Correções e regressão

- [ ] Decisão e justificativa para cada achado.
- [ ] Defeitos críticos e altos corrigidos.
- [ ] Melhorias aceitas implementadas.
- [ ] Sugestões adiadas ou recusadas justificadas.
- [ ] Fluxos afetados retestados.
- [ ] Suíte completa e CI aprovadas.
- [ ] Nenhuma migração pendente.
- [ ] Checklist acadêmico atualizado.

## Gate E — Entrega final

- [ ] Screenshots da tag final inseridas no manual.
- [ ] PDF com as cinco opiniões e decisões gerado.
- [ ] Relatório acadêmico final revisado.
- [ ] `develop` integrada à `main`.
- [ ] Tag `v1.0.0` e release publicadas.
- [ ] VPS executando exatamente a tag final.
- [ ] Vídeo narrado gravado com a mesma versão.
- [ ] Duração do vídeo conferida em cinco minutos.
- [ ] Links de repositório, aplicação, PDF e vídeo testados.

## Regra de promoção

Não promover para `main` nem criar a tag final enquanto houver avaliação pendente, defeito crítico
ou alto aberto, evidência sem anonimização ou divergência entre aplicação e documentação.
