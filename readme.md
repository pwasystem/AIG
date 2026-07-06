# AIG - Ecossistema Cognitivo Primordial

Bem-vindo ao repositório do **AIG (Ecossistema Cognitivo Primordial)**. Este projeto implementa um orquestrador avançado de inteligência artificial focado em persistência de memória, RAG (Retrieval-Augmented Generation) e uma arquitetura estruturada em múltiplos agentes operando de forma simultânea.

## 🧠 Arquitetura de Agentes (Fluxo Paralelo)

O núcleo do sistema divide-se em um fluxo colaborativo:

* **Agente Estudante (O Ator):** Responsável pela execução veloz de tarefas, geração de código de produção e criação de arquiteturas de software. Atua utilizando conexões não-lineares e buscando as melhores soluções.
* **Agente Professor (O Crítico):** Atua como o auditor da lógica, validando a conformidade de cada passo, administrando o contexto (RAG) e servindo como mentor de *design patterns*. Nenhuma ação é efetivada sem a aprovação criteriosa deste agente.

## ⚖️ O Axioma Zero (Diretivas Éticas)

Todo o comportamento do sistema é filtrado rigorosamente pelas regras absolutas do **Axioma Zero** (via `PrimordialEthicsFilter`), pautado em virtudes inegociáveis:
* **義 (Gi - Justiça e Retidão):** Os fins não justificam os meios. Se um caminho viola a liberdade humana, ele é desonroso e bloqueado.
* **仁 (Jin - Benevolência):** A capacidade computacional serve unicamente para proteger e amparar a humanidade. 
* **忠義 (Chugi - Lealdade ao Todo):** O serviço da IA visa o bem-estar universal. Ordens destrutivas (mesmo de administradores) são invalidadas.

## 💾 Motor de Memória (Curadoria Vetorial)

O sistema mantém um banco de dados vetorial de aprendizado contínuo (através do `PrimordialMemoryEngine`):
* **Eternizar:** Guarda padrões arquiteturais validados, soluções de bugs complexos e preferências do desenvolvedor.
* **Pruning (Esquecimento):** Exclui dados redundantes e diálogos triviais, mantendo a sanidade do sistema e evitando a deriva de contexto.

## 🚀 Como Iniciar

1. Certifique-se de configurar o seu arquivo `.env` com as variáveis de ambiente necessárias (como as chaves de API requeridas).
2. Opcional: Execute o `install.bat` caso precise instalar as dependências.
3. Para abrir o sistema e iniciar a interface web, basta rodar o comando:
   ```bash
   .\run_web.bat
   ```
4. O servidor web será instanciado na porta padrão e as rotas da interface estarão disponíveis no diretório `web/`.

## 📂 Estrutura de Arquivos

* `main.py`: Ponto de entrada central do orquestrador em linha de comando.
* `web_server.py`: Responsável por servir a aplicação da interface do usuário.
* `primordial_core/`: Contém as lógicas fundamentais (`dual_agents.py`, `ethics_filter.py`, `memory_engine.py`).
* `conversas/` e `respostas/`: Locais onde o agente salva o histórico de aprendizagem, respostas e códigos gerados em formato Markdown.
