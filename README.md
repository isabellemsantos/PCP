# PCP – Sistema de Controle de Pedidos de Produção

Sistema web local para acompanhar pedidos de produção: cadastro de pedidos, status por setor, datas de entrega, previsão de retorno, histórico de alterações e backup automático dos dados.

## Stack técnica

- **Backend:** Python (Flask)
- **Banco de dados:** SQLite
- **Frontend:** HTML/JS (`pcp_prototype.html`, `pcp_prototype_sqlite.html`)
- **Controle de versão:** Git + GitHub
- **Desenvolvimento assistido por IA:** Claude (protótipo inicial), ChatGPT (iterações e melhorias), Claude Code (edição direta do código e automação das rotinas de Git)

## Funcionalidades

- Cadastro e edição de pedidos (cliente, quantidade faltante, datas de entrega, previsão de retorno, status/setor)
- Controle de acesso por papel: leitura (Vendas/Expedição) e edição (PCP)
- Importação e exportação de dados via Excel (`/api/import.xlsx`)
- Backup automático diário do banco de dados e da planilha
- Log de auditoria de todas as alterações

## Como rodar

1. Instalar as dependências:
   ```
   pip install -r requirements_pcp.txt
   ```
2. Rodar o servidor:
   ```
   iniciar_pcp.bat
   ```
   (ou `python servidor_pcp.py` diretamente)
3. Acessar no navegador: `http://localhost:8080`

## Sobre este projeto

Este sistema foi criado para resolver um problema concreto do setor de PCP (Planejamento e Controle de Produção) da MTR Topura Fastener do Brasil: o acompanhamento de ordens de fabricação — quantidade faltante, cliente, data de entrega, previsão de retorno e status por setor — era feito manualmente em planilhas, sem histórico de alterações e sujeito a divergências entre quem consultava e quem atualizava.

O sistema roda como um servidor local acessível pela rede da empresa, permitindo que times diferentes (Vendas, Expedição e PCP) consultem os mesmos pedidos em tempo real, cada um com o nível de acesso adequado (leitura ou edição). Ele convive com o ERP Omega já usado pela empresa, cobrindo o acompanhamento detalhado de pedidos que o ERP não centraliza da mesma forma.

Autora e responsável pela manutenção: Isabelle Mendonça, Auxiliar Administrativa do setor de PCP, sem formação em desenvolvimento de software. O projeto foi construído do zero com apoio de ferramentas de IA como parceiras de desenvolvimento:

- **Claude** desenhou a arquitetura inicial e o protótipo funcional (backend, banco de dados e interface)
- **ChatGPT** tem sido usado nas melhorias e ajustes do dia a dia
- **Claude Code** foi incorporado para editar o código diretamente, sem precisar copiar/colar arquivos manualmente, e para automatizar as rotinas de controle de versão (Git/GitHub)

Isso permitiu que uma pessoa da área administrativa, sem background técnico, entregasse e mantivesse um sistema de produção real — incluindo boas práticas como backup automático diário, log de auditoria de mudanças e proteção de dados sensíveis (banco de dados e planilhas reais ficam fora do controle de versão, ver `.gitignore`).
