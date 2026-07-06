import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Reconfigura as saídas padrão para UTF-8 no Windows para evitar erros com emojis
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import chromadb
from chromadb.utils import embedding_functions


class PrimordialMemoryEngine:
    def __init__(self, db_path: str = "./.antigravity/primordial_vector_db"):
        """
        Inicializa o banco de dados vetorial local usando o ChromaDB.
        Configura uma coleção dedicada para as memórias de longo prazo da AGI.
        """
        # Garante que a pasta de destino exista dentro do ambiente oculto
        os.makedirs(db_path, exist_ok=True)
        
        # Inicializa o cliente persistente do ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Usamos a função de embedding padrão e leve do ChromaDB (All-MiniLM-L6-v2)
        # Ela transforma textos em vetores matemáticos localmente na máquina
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Cria ou recupera a coleção de memórias estáveis
        self.collection = self.chroma_client.get_or_create_collection(
            name="primordial_long_term_memory",
            embedding_function=self.embedding_function
        )
        print("🧠 [DATABASE]: Motor de Memória Vetorial ChromaDB inicializado com sucesso.")

    def eternizar_memoria(self, categoria: str, conteudo: str, tags: List[str]):
        """
        Salva uma nova informação estrutural filtrada e aprovada pelo Agente Professor.
        Armazena o texto e gera o vetor matemático automaticamente.
        """
        timestamp = datetime.now().isoformat()
        # Gera um ID único baseado no timestamp atual
        memoria_id = f"mem_{int(datetime.now().timestamp() * 1000)}"
        
        metadata = {
            "timestamp": timestamp,
            "category": categoria,
            "tags": ",".join(tags)
        }
        
        # Injeta o documento de texto no banco vetorial
        self.collection.add(
            documents=[conteudo],
            metadatas=[metadata],
            ids=[memoria_id]
        )
        print(f"📦 [RAG VETORIAL]: Nova memória integrada permanentemente. Categoria: '{categoria}'.")

    def buscar_contexto_por_analogia(self, prompt_usuario: str, limite: int = 3) -> str:
        """
        Realiza uma busca semântica (por proximidade matemática).
        Encontra conceitos correlacionados ou analogias distantes que ajudem o Estudante.
        """
        # Se a coleção estiver vazia, evita o erro de busca
        if self.collection.count() == 0:
            return "Nenhum histórico ou padrão arquitetural registrado na memória de longo prazo ainda."
            
        # Faz a query vetorial baseada no significado da frase do usuário
        results = self.collection.query(
            query_texts=[prompt_usuario],
            n_results=limite
        )
        
        if not results or not results['documents'] or not results['documents'][0]:
            return "Nenhuma analogia relevante encontrada no banco de dados vetorial."
            
        formatted_memories = []
        # Desempacota os documentos e metadados encontrados
        for idx, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][idx]
            formatted_memories.append(
                f"[{meta['timestamp']}] (Categoria: {meta['category']}) (Tags: {meta['tags']}):\n{doc}"
            )
            
        return "\n\n---\n\n".join(formatted_memories)

    def esquecimento_deliberado_pruning(self, tag_ou_id_palavra: str):
        """
        Executa a rotina de limpeza comandada pelo Professor.
        Remove memórias que provaram ser obsoletas, incorretas ou ruídos contraditórios.
        """
        if self.collection.count() == 0:
            return
            
        # Deleta registros que correspondam a uma tag específica para limpar o contexto
        self.collection.delete(where={"tags": tag_ou_id_palavra})
        print(f"✂️ [PRUNING]: Memórias antigas com a tag '{tag_ou_id_palavra}' foram expurgadas do sistema.")

# Teste local rápido para garantir o funcionamento do motor vetorial
if __name__ == "__main__":
    engine = PrimordialMemoryEngine()
    # Teste de inserção
    engine.eternizar_memoria(
        categoria="Arquitetura/Segurança",
        conteudo="Padrão estabelecido pelo usuário Luiz: Utilizar sempre criptografia AES-GCM com chaves de 256 bits geradas de forma randômica por os.urandom().",
        tags=["segurança", "aes-gcm", "criptografia"]
    )
    # Teste de busca por analogia (frase diferente, mesmo significado)
    print("\n🔍 Testando busca por afinidade conceitual:")
    contexto = engine.buscar_contexto_por_analogia("Como devo codificar a proteção de dados privados dos arquivos?")
    print(contexto)