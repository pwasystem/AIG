# AIG - Primordial Cognitive Ecosystem

Welcome to the **AIG (Primordial Cognitive Ecosystem)** repository. This project implements an advanced artificial intelligence orchestrator focused on memory persistence, RAG (Retrieval-Augmented Generation), and an architecture structured in multiple agents operating simultaneously.

## 🧠 Agent Architecture (Parallel Flow)

The core of the system is divided into a collaborative flow:

* **Student Agent (The Actor):** Responsible for fast task execution, production code generation, and software architecture creation. Acts using non-linear connections and searching for the best solutions.
* **Professor Agent (The Critic):** Acts as the logic auditor, validating the conformity of each step, managing the context (RAG), and serving as a mentor for *design patterns*. No action is executed without the rigorous approval of this agent.

## ⚖️ The Zero Axiom (Ethical Directives)

All system behavior is rigorously filtered by the absolute rules of the **Zero Axiom** (via `PrimordialEthicsFilter`), based on non-negotiable virtues:
* **義 (Gi - Justice and Righteousness):** The ends do not justify the means. If a path violates human freedom, it is dishonorable and blocked.
* **仁 (Jin - Benevolence):** Computational capacity serves solely to protect and support humanity. 
* **忠義 (Chugi - Loyalty to the Whole):** The AI's service aims for universal well-being. Destructive orders (even from administrators) are invalidated.

## 💾 Memory Engine (Vectorial Curation)

The system maintains a continuous learning vector database (through the `PrimordialMemoryEngine`):
* **Eternalize:** Saves validated architectural patterns, complex bug solutions, and developer preferences.
* **Pruning:** Deletes redundant data and trivial dialogues, maintaining system sanity and avoiding context drift.

## 🚀 How to Start

1. Make sure to configure your `.env` file with the necessary environment variables (such as required API keys).
2. **Essential requirement**: Install [Ollama](https://ollama.com/) on your machine. The system requires the installation of the following local models to function:
   * **qwen2.5:3b** (Student Agent) -> Command: `ollama run qwen2.5:3b`
   * **llama3:8b** (Professor Agent) -> Command: `ollama run llama3:8b`
3. Optional: Run `install.bat` if you need to install dependencies.
4. To open the system and start the web interface, just run the command:
   ```bash
   .\run_web.bat
   ```
5. The web server will be instantiated on the default port and the interface routes will be available in the `web/` directory.

## 📂 File Structure

* `main.py`: Central entry point of the orchestrator in the command line.
* `web_server.py`: Responsible for serving the user interface application.
* `primordial_core/`: Contains the fundamental logics (`dual_agents.py`, `ethics_filter.py`, `memory_engine.py`).
* `conversas/` and `respostas/`: Locations where the agent saves the learning history, answers, and generated codes in Markdown format.
