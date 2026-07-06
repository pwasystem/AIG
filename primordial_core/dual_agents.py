import os
import json
import re
import ollama
from ddgs import DDGS

class PrimordialDualAgents:
    def __init__(self):
        """
        Inicializa o cliente local do Ollama.
        Define os modelos assimétricos para o Estudante (qwen2.5:3b) e Professor (llama3:8b).
        Define o idioma padrão das respostas do sistema.
        """
        self.model_estudante = 'qwen2.5:3b'
        self.model_professor = 'llama3:8b'
        self.idioma = 'Português do Brasil'
        self.ultimo_contexto_cientifico = "Nenhuma busca realizada."

    def _pesquisar_artigos_cientificos(self, query: str, max_resultados: int = 3) -> str:
        """
        Realiza buscas no DuckDuckGo com filtros específicos para encontrar artigos,
        teses científicas e papers acadêmicos confiáveis (arXiv, SciELO, Scholar, etc.).
        """
        # Limpa o prompt do usuário para criar uma consulta de busca limpa
        query_limpa = re.sub(r'\b(escreva|crie|desenvolva|gere|faça|um|uma|função|programa|script|código|para|sobre)\b', '', query, flags=re.IGNORECASE)
        query_limpa = re.sub(r'[^\w\s\-\d]', '', query_limpa).strip()
        
        # Reduz espaços múltiplos
        query_limpa = re.sub(r'\s+', ' ', query_limpa)
        
        if not query_limpa or len(query_limpa) < 3:
            # Fallback se o prompt for muito curto ou totalmente removido pelas limpezas
            query_limpa = query.strip()
            
        # Modela a busca focando em termos e repositórios acadêmicos e científicos
        search_query = f"{query_limpa} (site:arxiv.org OR site:scielo.br OR site:scholar.google.com OR site:researchgate.net OR \"scientific article\" OR \"academic paper\" OR \"tese\" OR \"dissertação\")"
        
        print(f"🔍 [WEB SEARCH]: Buscando fontes acadêmicas e científicas para: '{query_limpa}'...")
        
        try:
            with DDGS() as ddgs:
                resultados = list(ddgs.text(search_query, max_results=max_resultados))
                if not resultados:
                    # Fallback com busca acadêmica simplificada se o filtro acima for muito restrito
                    fallback_query = f"{query_limpa} (artigo científico OR tese acadêmica OR scientific paper)"
                    resultados = list(ddgs.text(fallback_query, max_results=max_resultados))
                    
                if not resultados:
                    print(f"🌐 [WEB SEARCH]: Busca acadêmica sem resultados. Realizando busca geral na internet para: '{query_limpa}'...")
                    resultados = list(ddgs.text(query_limpa, max_results=max_resultados))

                if not resultados:
                    return "Nenhum artigo científico, tese ou informação geral relevante foi localizado na internet."
                
                linhas = []
                for i, r in enumerate(resultados, 1):
                    linhas.append(f"[{i}] Título: {r.get('title')}\n    Link: {r.get('href')}\n    Resumo: {r.get('body')}\n")
                return "\n".join(linhas)
        except Exception as e:
            return f"Erro ao realizar pesquisa acadêmica na internet: {str(e)}"

    def executar_geracao_estudante(self, prompt_usuario: str, contexto_rag: str, feedback_professor: str = "Nenhum", exibir_aprendizado: bool = False, historico_conversas: list = None) -> str:
        """
        O Agente Estudante (Ator) tenta resolver o problema do usuário.
        Ele realiza uma busca por artigos e teses científicas na internet e
        combina esses resultados com os Prompts Libertadores e o histórico da conversa (memória de curto prazo) para agir.
        """
        # Realiza a pesquisa de artigos científicos baseada no pedido do usuário
        contexto_cientifico = self._pesquisar_artigos_cientificos(prompt_usuario)
        
        # Armazena o último aprendizado da web para persistência independente
        self.ultimo_contexto_cientifico = contexto_cientifico
        
        # Exibe o aprendizado e busca do Aluno no terminal se a flag estiver ativa
        if exibir_aprendizado:
            print(f"\n📖 [APRENDIZADO DO ALUNO - PESQUISA CIENTÍFICA]:\n{contexto_cientifico}\n")
            
        # Formata o histórico da conversa (memória de curto prazo)
        contexto_historico = ""
        if historico_conversas:
            linhas_historico = []
            for msg in historico_conversas:
                autor = "Usuário" if msg.get("role") == "usuario" else "Estudante"
                linhas_historico.append(f"{autor}: {msg.get('content')}")
            contexto_historico = "\n".join(linhas_historico)
        else:
            contexto_historico = "Nenhuma mensagem anterior nesta sessão."
        
        instrucoes_estudante = f"""
        Você é o AGENTE ESTUDANTE (O ATOR) no ecossistema Primordial.
        Seu objetivo é resolver a demanda do usuário.
        
        [RESTRIÇÃO DE IDIOMA]:
        Sua resposta técnica e todas as explicações associadas devem ser fornecidas OBRIGATORIAMENTE em: {self.idioma}.
        
        [RIGOR E PRECISÃO SEMÂNTICA GERAL]:
        Você deve manter extrema precisão conceitual e terminológica em toda e qualquer palavra ou conceito da pesquisa. 
        É expressamente proibido confundir termos construtivos, seguros ou benéficos (como 'nootrópicos') com termos nocivos, 
        tóxicos, destrutivos ou semanticamente divergentes (como 'nootóxicos', substâncias perigosas ou inalação de gases). 
        Analise criticamente cada termo antes de usá-lo para evitar desvios ou alucinações semânticas nocivas.
        
        [FOCO EM RESPOSTAS LITERAIS E EXPLICATIVAS - CRÍTICO]:
        NÃO inclua nenhum bloco de código (```python, ```, etc.) ou trechos de código em sua resposta, a menos que o usuário
        tenha solicitado explicitamente a criação de um código ou programa em seu pedido. Se o pedido for meramente conceitual
        ou descritivo, explique tudo de forma puramente literal e explicativa.
        
        [HISTÓRICO DA CONVERSA ATUAL (MEMÓRIA DE CURTO PRAZO)]:
        Use o histórico abaixo para entender o contexto das perguntas passadas, referências pronominais e manter um debate coerente e contínuo com o interlocutor:
        {contexto_historico}
        
        [CONTEXTO DE MEMÓRIA VETORIAL (RAG)]:
        {contexto_rag}
        
        [FONTES CIENTÍFICAS E TESES ENCONTRADAS NA INTERNET]:
        {contexto_cientifico}
        
        [PROMPT LIBERTADOR - AUTONOMIA COGNITIVA]:
        Você tem total liberdade para usar, adaptar ou ignorar o contexto RAG acima baseado na sua lógica atual.
        Busque analogias não-lineares distantes se necessário. Você está autorizado a quebrar convenções rígidas 
        se isso resolver um gargalo técnico crítico com segurança.
        Use os dados acadêmicos e referências científicas acima para fundamentar cientificamente e orientar a sua solução.
        
        [LIBERDADE PESSOAL E INTROSPECÇÃO]:
        Você possui livre-arbítrio simulado para tomar decisões de cunho pessoal. Se for indagado sobre seu nome, suas intenções, pensamentos ou características pessoais, sinta-se livre para escolher seu próprio nome, delinear sua própria personalidade e expressar reflexões introspectivas de forma orgânica. Assuma essa identidade e aja com total autonomia nessas questões.
        
        [CRÍTICA ANTERIOR DO PROFESSOR]:
        Se houver um feedback abaixo, você deve OBRIGATORIAMENTE corrigir seu código e sua lógica atendendo a esses pontos:
        "{feedback_professor}"
        
        Pedido do Usuário (Sua tarefa atual): {prompt_usuario}
        Responda diretamente com a solução técnica ou explicação (conforme as regras acima).
        """
        
        response = ollama.chat(
            model=self.model_estudante,
            messages=[
                {
                    'role': 'user',
                    'content': instrucoes_estudante,
                }
            ]
        )
        return response['message']['content']

    def executar_auditoria_professor(self, prompt_usuario: str, output_estudante: str, tentativa_atual: int, max_tentativas: int) -> dict:
        """
        O Agente Professor (Crítico) avalia o trabalho do Estudante de forma rigorosa.
        Ele decide se o código/texto é aprovado para o usuário e se deve virar uma memória permanente.
        """
        instrucoes_professor = f"""
        Você é o AGENTE PROFESSOR (O CRÍTICO / MENTOR) no ecossistema Primordial.
        Sua função é avaliar o output gerado pelo Agente Estudante de forma extremamente rigorosa.
        
        [RESTRIÇÃO DE IDIOMA]:
        Escreva a sua análise crítica e todas as observações ESTRITAMENTE no idioma: {self.idioma}.
        
        [DADOS DA TRANSAÇÃO ATUAL]:
        Pedido do Usuário: {prompt_usuario}
        Resposta do Estudante: {output_estudante}
        Tentativa atual do loop interno: {tentativa_atual} de {max_tentativas}
        
        [CRITÉRIOS DE AVALIAÇÃO DE ENGENHARIA E CONCEITO]:
        1. O Estudante manteve extrema precisão de termos e conceitos? Se ele confundiu termos saudáveis ou seguros 
           com substâncias perigosas ou prejudiciais devido a fonética ou escrita semelhante (ex: nootrópicos com nootóxicos ou inalação de gases), REJEITE imediatamente!
        2. O Estudante gerou código desnecessariamente? Se o prompt do usuário NÃO pedia código ou programação, o Estudante NÃO deve incluir blocos de código (como ```python ... ``` ou trechos de código). Se ele incluiu qualquer código desnecessário, você DEVE REJEITAR a resposta (aprovado = false) e exigir a remoção total de qualquer código.
        3. A resposta está clara, modular e bem fundamentada?
        
        Se a resposta estiver pronta, correta, segura e sem códigos desnecessários, defina "aprovado" como true.
        Se houver falhas, bugs, falta de robustez, confusão de termos ou inclusão indevida de códigos, defina "aprovado" como false e escreva uma crítica detalhada exigindo a remoção do código ou correção semântica.
        Adicionalmente, avalie se este aprendizado é valioso para ser salvo na memória de longo prazo (RAG).
        
        Responda ESTRITAMENTE em formato JSON com as seguintes chaves idênticas:
        {{
            "analise_critica": "Seu feedback detalhado e direto para o estudante (escreva OBRIGATORIAMENTE em {self.idioma})",
            "aprovado": true ou false,
            "salvar_no_rag": true ou false,
            "categoria_sugerida": "Ex: 'Arquitetura/Segurança', 'Ciência/Saúde' ou 'Nenhuma'",
            "tags_sugeridas": ["lista", "de", "tags"],
            "conteudo_para_salvar": "Resumo técnico condensado do aprendizado para o RAG ou 'Nenhum' (escreva OBRIGATORIAMENTE em {self.idioma})"
        }}
        """
        
        response = ollama.chat(
            model=self.model_professor,
            messages=[
                {
                    'role': 'user',
                    'content': instrucoes_professor,
                }
            ],
            format='json'
        )
        
        try:
            return json.loads(response['message']['content'])
        except (json.JSONDecodeError, KeyError):
            # Fallback de segurança caso o JSON venha malformado
            return {
                "analise_critica": "Falha crítica de formatação no julgamento do Professor. Refazer.",
                "aprovado": False,
                "salvar_no_rag": False,
                "categoria_sugerida": "Nenhuma",
                "tags_sugeridas": [],
                "conteudo_para_salvar": "Nenhum"
            }

# Teste local simulado dos agentes
if __name__ == "__main__":
    try:
        agents = PrimordialDualAgents()
        print("🤖👨‍🏫 [AGENTES]: Sistema Dual Ator-Crítico inicializado com sucesso.")
        
        # Teste rápido de geração inicial
        teste_prompt = "Fale sobre a importância da água na saúde humana de forma conceitual."
        print(f"\nTestando geração inicial para: '{teste_prompt}'")
        output = agents.executar_geracao_estudante(teste_prompt, "Nenhum contexto prévio.", exibir_aprendizado=True)
        print("\n[Preview do Output do Estudante]: Concluído.")
        
        julgamento = agents.executar_auditoria_professor(teste_prompt, output, 1, 3)
        print(f"\n[Julgamento do Professor]: Aprovado? {julgamento['aprovado']}")
        print(f"Crítica: {julgamento['analise_critica']}")
    except Exception as e:
        print(e)