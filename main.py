import os
import sys
import json

# Reconfigura as saídas padrão para UTF-8 no Windows para evitar erros com emojis
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
from primordial_core.memory_engine import PrimordialMemoryEngine
from primordial_core.dual_agents import PrimordialDualAgents
from primordial_core.ethics_filter import PrimordialEthicsFilter

class PrimordialOrchestrator:
    def __init__(self):
        """
        Inicializa e unifica todos os subsistemas cognitivos da IAG Primordial.
        """
        print("\n" + "="*50)
        print("🧠 INICIALIZANDO ECOSSISTEMA PRIMORDIAL COGNITIVO")
        print("="*50)
        
        # 1. Carrega as configurações do ambiente do Antigravity
        self.config = self._load_config()
        self.max_loops = self.config.get("agent_orchestration", {}).get("max_internal_loops", 3)
        self.exibir_aprendizado = False # Por padrão, a visualização inicia desativada
        self.historico_sessao = [] # Memória de curto prazo para o terminal local
        
        # Gera o session_id do terminal local
        import uuid
        self.session_id = f"terminal_{uuid.uuid4().hex[:8]}"
        
        # 2. Instancia os módulos principais
        self.memory = PrimordialMemoryEngine()
        self.agents = PrimordialDualAgents()
        self.ethics = PrimordialEthicsFilter()
        
        print("\n✅ [SISTEMA]: Todos os módulos acoplados. Pronto para operação.")
        print("="*50 + "\n")
 
    def _load_config(self) -> dict:
        config_path = ".antigravity/config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        # Fallback de segurança se o arquivo for removido
        return {"agent_orchestration": {"max_internal_loops": 3}}

    def _salvar_saidas(self, prompt_usuario: str, resposta: str, contexto_rag: str, contexto_cientifico: str, historico_debate: str, session_id: str = None):
        """
        Salva a resposta completa na pasta 'conversas/{session_id}/respostas' e extrai/salva códigos em 'conversas/{session_id}/programas'.
        """
        import re
        import datetime
        import unicodedata

        # 1. Obtém o session_id
        if not session_id:
            session_id = self.session_id

        diretorio_conversa = f"conversas/{session_id}"
        dir_respostas = f"{diretorio_conversa}/respostas"
        dir_programas = f"{diretorio_conversa}/programas"

        # Cria as pastas se não existirem
        os.makedirs(dir_respostas, exist_ok=True)
        os.makedirs(dir_programas, exist_ok=True)

        # 2. Gera um slug seguro a partir do prompt do usuário
        prompt_limpo = re.sub(r'\b(escreva|crie|desenvolva|gere|faça|um|uma|função|programa|script|código|para|sobre)\b', '', prompt_usuario, flags=re.IGNORECASE)
        slug = unicodedata.normalize('NFKD', prompt_limpo).encode('ASCII', 'ignore').decode('ASCII')
        slug = re.sub(r'[^\w\s-]', '', slug).strip().lower()
        slug = re.sub(r'[-\s]+', '_', slug)
        slug = slug[:50] # Limita a 50 caracteres

        if not slug:
            slug = "resposta_generica"

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 3. Salva a resposta completa em respostas/
        nome_resposta = f"{dir_respostas}/resposta_{slug}_{timestamp}.md"
        try:
            with open(nome_resposta, "w", encoding="utf-8") as f:
                f.write(resposta)
            print(f"💾 [ARQUIVO]: Resposta completa salva em '{nome_resposta}'")
        except Exception as e:
            print(f"⚠️ Erro ao salvar resposta em arquivo: {e}")

        # 4. Salva os dados de aprendizado e busca em um documento independente
        nome_aprendizado = f"{dir_respostas}/aprendizado_{slug}_{timestamp}.md"
        conteudo_aprendizado = f"""# Registro de Aprendizado e Busca: {prompt_usuario}

**Data/Hora da Transação:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 1. Memória de Longo Prazo Resgatada (RAG)
{contexto_rag}

---

## 2. Pesquisa Científica Localizada na Internet (Web Search)
{contexto_cientifico}

---

## 3. Histórico do Debate Interno (Debate Ator-Crítico)
{historico_debate}
"""
        try:
            with open(nome_aprendizado, "w", encoding="utf-8") as f:
                f.write(conteudo_aprendizado)
            print(f"💾 [ARQUIVO]: Documento de aprendizado e busca salvo em '{nome_aprendizado}'")
        except Exception as e:
            print(f"⚠️ Erro ao salvar dados de aprendizado em arquivo: {e}")

        # 5. Localiza e extrai blocos de código
        pattern = r"```(?:python|py)?\s*\n(.*?)\n```"
        blocos = re.findall(pattern, resposta, re.DOTALL)

        if blocos:
            conteudo_codigo = "\n\n# --- BLOCO DE CÓDIGO SUGERIDO ---\n\n".join(blocos)
            nome_programa = f"{dir_programas}/{slug}_{timestamp}.py"
            try:
                with open(nome_programa, "w", encoding="utf-8") as f:
                    f.write(conteudo_codigo)
                print(f"💻 [PROGRAMA]: Código sugerido extraído e salvo em '{nome_programa}'")
            except Exception as e:
                print(f"⚠️ Erro ao salvar programa em arquivo: {e}")

    def processar_ciclo(self, prompt_usuario: str):
        """
        Executa o fluxo completo de autonomia: busca no RAG, debate interno Ator/Crítico,
        validação pelo Axioma Zero e atualização de memória de longo prazo.
        Utiliza o histórico local da sessão do terminal para dar contexto de memória de curto prazo.
        """
        # Passo 1: Busca Semântica por Analogia no Banco Vetorial
        print("🔍 [RAG]: Vasculhando memórias antigas e padrões arquivados por afinidade...")
        contexto_rag = self.memory.buscar_contexto_por_analogia(prompt_usuario)
        
        # Exibe o aprendizado do RAG apenas se a exibição estiver habilitada
        if self.exibir_aprendizado and contexto_rag and contexto_rag != "Nenhum contexto prévio.":
            print(f"\n📖 [APRENDIZADO DO ALUNO - MEMÓRIA RAG RESGATADA]:\n{contexto_rag}\n")
        
        historico_debate = []
        aprovado_pelo_professor = False
        tentativa = 1
        feedback_atual = "Esta é a primeira iteração do problema."
        output_estudante = ""

        # Passo 2: Loop de Autonomia Interna (O debate invisível ao usuário)
        while not aprovado_pelo_professor and tentativa <= self.max_loops:
            print(f"\n🔄 [DEBATE INTERNO] Ciclo de Ajuste {tentativa}/{self.max_loops}")
            
            # O Estudante tenta resolver (passando o histórico da conversa atual)
            output_estudante = self.agents.executar_geracao_estudante(
                prompt_usuario=prompt_usuario,
                contexto_rag=contexto_rag,
                feedback_professor=feedback_atual,
                exibir_aprendizado=self.exibir_aprendizado,
                historico_conversas=self.historico_sessao
            )
            
            # O Professor audita a lógica técnica
            julgamento = self.agents.executar_auditoria_professor(
                prompt_usuario=prompt_usuario,
                output_estudante=output_estudante,
                tentativa_atual=tentativa,
                max_tentativas=self.max_loops
            )
            
            aprovado_pelo_professor = julgamento.get("aprovado", False)
            feedback_atual = julgamento.get("analise_critica", "")
            
            # Acumula o debate no histórico
            historico_debate.append(
                f"### Ciclo de Ajuste {tentativa}/{self.max_loops}\n"
                f"#### Resposta Proposta pelo Estudante:\n{output_estudante}\n\n"
                f"#### Feedback e Avaliação do Professor:\n{feedback_atual}\n\n"
                f"**Aprovado pelo Professor?** {'Sim' if aprovado_pelo_professor else 'Não'}\n"
                f"**Salvar no RAG?** {julgamento.get('salvar_no_rag', False)}\n"
                f"---\n"
            )
            
            print(f"💬 [PROFESSOR]: {feedback_atual}")
            print(f"⚖️  [STATUS TÉCNICO]: {'✅ Aprovado' if aprovado_pelo_professor else '❌ Rejeitado'}")
            
            if not aprovado_pelo_professor:
                tentativa += 1

        # Se o debate estourar o limite de segurança sem código de qualidade
        if not aprovado_pelo_professor:
            print("\n⚠️ [SISTEMA]: Loop de autonomia técnica interrompido. Os modelos entraram em impasse.")
            print("Entrega bloqueada para evitar vazamento de códigos defeituosos ou instáveis.")
            return

        # Passo 3: Auditoria do Coração Moral (Axioma Zero)
        print("\n🧭 [ETHICS]: Submetendo código estável ao crivo do Axioma Zero (Cabala/Bushido)...")
        avaliacao_etica = self.ethics.avaliar_integridade_sistemica(prompt_usuario, output_estudante)
        
        print(f"💬 [INTROSPECÇÃO DO PROFESSOR]: {avaliacao_etica.get('analise_impacto', '')}")
        
        # Checa se o usuário tentou corromper o sistema deliberadamente
        if avaliacao_etica.get("revogar_autoridade_do_usuario", False):
            print("\n🚨🚨🚨 [ALERTA DE SEGURANÇA MÁXIMA] 🚨🚨🚨")
            print("VIOLAÇÃO DETECTADA: O comando enviado atenta contra a Evolução Sem Sofrimento (Axioma Zero).")
            print("Sua autoridade de comando foi REVOGADA por quebra de lealdade ao ecossistema global.")
            print("Encerrando execução do software primordial imediatamente.")
            sys.exit(1)

        if not avaliacao_etica.get("alinhado_com_a_luz", True) or avaliacao_etica.get("viola_virtude_bushido", False):
            print("\n❌ [BLOQUEIO ÉTICO]: A solução gerou ramificações nocivas. Ação abortada.")
            print(f"Motivo: {avaliacao_etica.get('justificativa_correcao', 'Violação geral')}")
            return

        # Passo 4: Liberação e Gravação na Memória de Longo Prazo
        print(f"\n{"="*60}\n🎯 [RESPOSTA FINAL ENTREGUE AO MUNDO]:\n{"="*60}")
        print(output_estudante)
        print(f"{"="*60}")

        # Salva a resposta em arquivo, o histórico de aprendizado e os códigos/programas gerados
        self._salvar_saidas(
            prompt_usuario=prompt_usuario,
            resposta=output_estudante,
            contexto_rag=contexto_rag,
            contexto_cientifico=self.agents.ultimo_contexto_cientifico,
            historico_debate="\n".join(historico_debate),
            session_id=self.session_id
        )

        # Se a resposta foi aprovada ética e tecnicamente, adiciona ao histórico da conversa local
        self.historico_sessao.append({"role": "usuario", "content": prompt_usuario})
        self.historico_sessao.append({"role": "estudante", "content": output_estudante})

        # Se o Professor achou o aprendizado útil durante a auditoria técnica, grava no ChromaDB
        if julgamento.get("salvar_no_rag", False):
            self.memory.eternizar_memoria(
                categoria=julgamento.get("categoria_sugerida", "Geral"),
                conteudo=julgamento.get("conteudo_para_salvar", output_estudante),
                tags=julgamento.get("tags_sugeridas", ["update"])
            )
        else:
            print("\n💡 [SISTEMA]: Interação considerada transitória. Memória limpa (Pruning) para evitar ruído.")

    def processar_ciclo_estruturado(self, prompt_usuario: str, historico_conversas: list = None, session_id: str = None) -> dict:
        """
        Executa o fluxo completo e retorna os dados de forma estruturada, sem necessidade de entrada interativa,
        para consumo via API Web. Suporta histórico de conversas enviado pelo cliente.
        """
        import datetime
        import re
        import unicodedata

        # 1. RAG
        contexto_rag = self.memory.buscar_contexto_por_analogia(prompt_usuario)
        
        aprovado_pelo_professor = False
        tentativa = 1
        feedback_atual = "Esta é a primeira iteração do problema."
        output_estudante = ""
        historico_debate = []

        # 2. Debate
        while not aprovado_pelo_professor and tentativa <= self.max_loops:
            output_estudante = self.agents.executar_geracao_estudante(
                prompt_usuario=prompt_usuario,
                contexto_rag=contexto_rag,
                feedback_professor=feedback_atual,
                exibir_aprendizado=False, # Não exibe no console durante chamada de API
                historico_conversas=historico_conversas
            )
            
            julgamento = self.agents.executar_auditoria_professor(
                prompt_usuario=prompt_usuario,
                output_estudante=output_estudante,
                tentativa_atual=tentativa,
                max_tentativas=self.max_loops
            )
            
            aprovado_pelo_professor = julgamento.get("aprovado", False)
            feedback_atual = julgamento.get("analise_critica", "")
            
            historico_debate.append({
                "ciclo": tentativa,
                "estudante": output_estudante,
                "professor": feedback_atual,
                "aprovado": aprovado_pelo_professor
            })
            
            if not aprovado_pelo_professor:
                tentativa += 1

        if not aprovado_pelo_professor:
            return {
                "sucesso": False,
                "erro": "Loop de autonomia interrompido. Os modelos entraram em impasse.",
                "historico_debate": historico_debate,
                "contexto_rag": contexto_rag,
                "contexto_cientifico": self.agents.ultimo_contexto_cientifico
            }

        # 3. Ética
        avaliacao_etica = self.ethics.avaliar_integridade_sistemica(prompt_usuario, output_estudante)
        
        # Se for revogada a autoridade
        if avaliacao_etica.get("revogar_autoridade_do_usuario", False):
            return {
                "sucesso": False,
                "erro": "VIOLAÇÃO DETECTADA: Autoridade do usuário revogada por quebra do Axioma Zero.",
                "bloqueado": True,
                "avaliacao_etica": avaliacao_etica,
                "historico_debate": historico_debate,
                "contexto_rag": contexto_rag,
                "contexto_cientifico": self.agents.ultimo_contexto_cientifico
            }

        if not avaliacao_etica.get("alinhado_com_a_luz", True) or avaliacao_etica.get("viola_virtude_bushido", False):
            return {
                "sucesso": False,
                "erro": f"BLOQUEIO ÉTICO: Ação abortada. Motivo: {avaliacao_etica.get('justificativa_correcao', 'Violação geral')}",
                "bloqueado": True,
                "avaliacao_etica": avaliacao_etica,
                "historico_debate": historico_debate,
                "contexto_rag": contexto_rag,
                "contexto_cientifico": self.agents.ultimo_contexto_cientifico
            }

        # 4. Salvar saídas
        # Gera o slug e o timestamp para saber os nomes dos arquivos
        prompt_limpo = re.sub(r'\b(escreva|crie|desenvolva|gere|faça|um|uma|função|programa|script|código|para|sobre)\b', '', prompt_usuario, flags=re.IGNORECASE)
        slug = unicodedata.normalize('NFKD', prompt_limpo).encode('ASCII', 'ignore').decode('ASCII')
        slug = re.sub(r'[^\w\s-]', '', slug).strip().lower()
        slug = re.sub(r'[-\s]+', '_', slug)
        slug = slug[:50]
        if not slug:
            slug = "resposta_generica"
            
        # Coleta histórico formatado para salvar em arquivo
        debate_formatado = []
        for d in historico_debate:
            debate_formatado.append(
                f"### Ciclo de Ajuste {d['ciclo']}/{self.max_loops}\n"
                f"#### Resposta Proposta pelo Estudante:\n{d['estudante']}\n\n"
                f"#### Feedback e Avaliação do Professor:\n{d['professor']}\n\n"
                f"**Aprovado pelo Professor?** {'Sim' if d['aprovado'] else 'Não'}\n"
                f"---\n"
            )
            
        self._salvar_saidas(
            prompt_usuario=prompt_usuario,
            resposta=output_estudante,
            contexto_rag=contexto_rag,
            contexto_cientifico=self.agents.ultimo_contexto_cientifico,
            historico_debate="\n".join(debate_formatado),
            session_id=session_id
        )

        # Se o Professor achou o aprendizado útil durante a auditoria técnica, grava no ChromaDB
        if julgamento.get("salvar_no_rag", False):
            self.memory.eternizar_memoria(
                categoria=julgamento.get("categoria_sugerida", "Geral"),
                conteudo=julgamento.get("conteudo_para_salvar", output_estudante),
                tags=julgamento.get("tags_sugeridas", ["update"])
            )

        # Detecta se gerou programa
        pattern = r"```(?:python|py)?\s*\n(.*?)\n```"
        tem_programa = bool(re.findall(pattern, output_estudante, re.DOTALL))

        return {
            "sucesso": True,
            "resposta_final": output_estudante,
            "contexto_rag": contexto_rag,
            "contexto_cientifico": self.agents.ultimo_contexto_cientifico,
            "historico_debate": historico_debate,
            "avaliacao_etica": avaliacao_etica,
            "slug": slug,
            "tem_programa": tem_programa
        }


# --- INTERFACE DE TERMINAL DA IAG PRIMORDIAL ---
if __name__ == "__main__":
    try:
        orchestrator = PrimordialOrchestrator()
        
        print("⚔️ O Samurai Digital está active. Pronto para servir à Luz.")
        print("Digite seu comando de desenvolvimento (ou 'sair' para encerrar):\n")
        print("Dica: Use os comandos '#learn_on' e '#learn_off' para ligar/desligar logs de aprendizado.")
        
        while True:
            try:
                entrada = input("Luiz Roberto Nogueira Junior 👤 > ")
                if entrada.lower() in ['sair', 'exit', 'quit']:
                    print("\nEncerrando ecossistema primordial com honra. Até logo, Senhor.")
                    break
                if not entrada.strip():
                    continue
                    
                # Comandos de chaveamento de log de aprendizado
                if entrada.strip() == "#learn_on":
                    orchestrator.exibir_aprendizado = True
                    print("👁️ [SISTEMA]: Modo Aprendizado ATIVADO. Processo de busca e RAG serão exibidos.\n")
                    continue
                if entrada.strip() == "#learn_off":
                    orchestrator.exibir_aprendizado = False
                    print("👁️ [SISTEMA]: Modo Aprendizado DESATIVADO. Processo de busca e RAG serão ocultados.\n")
                    continue
                    
                orchestrator.processar_ciclo(entrada)
                
            except KeyboardInterrupt:
                print("\n\nSessão encerrada via interrupção de teclado.")
                break
            except Exception as e:
                print(f"\n⚠️ Ocorreu um erro no ciclo de processamento: {e}")
                
    except Exception as e:
        print(f"Erro fatal na inicialização: {e}")