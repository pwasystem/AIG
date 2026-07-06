import os
import sys
import uuid
import datetime
import re
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from main import PrimordialOrchestrator

app = FastAPI(title="AGI Primordial Web Server", version="1.0.0")

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o Orquestrador Primordial
orchestrator = PrimordialOrchestrator()

# Dicionário de sessões em memória
sessoes = {}

@app.post("/api/chat")
async def chat_endpoint(data: dict = Body(...)):
    session_id = data.get("session_id")
    message = data.get("message")
    
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="A mensagem do usuário não pode estar vazia.")
        
    # Gera uma nova sessão se não fornecida
    if not session_id or session_id not in sessoes:
        session_id = str(uuid.uuid4())
        sessoes[session_id] = []
        
    # Histórico de conversas da sessão atual
    historico = sessoes[session_id]
    
    # Processa o ciclo de agentes de forma estruturada passando o histórico e o session_id
    print(f"📥 [API]: Recebido prompt para sessão {session_id}: '{message}'")
    resultado = orchestrator.processar_ciclo_estruturado(message, historico_conversas=historico, session_id=session_id)
    
    if resultado.get("sucesso"):
        # Atualiza a memória de curto prazo (histórico de conversas) no servidor
        historico.append({"role": "usuario", "content": message})
        historico.append({"role": "estudante", "content": resultado.get("resposta_final")})
        
    return JSONResponse(content={
        "session_id": session_id,
        "resultado": resultado
    })

@app.post("/api/chat/reset")
async def reset_chat_endpoint(data: dict = Body(...)):
    session_id = data.get("session_id")
    if session_id in sessoes:
        sessoes[session_id] = []
        print(f"🧹 [API]: Redefinida a sessão de conversa: {session_id}")
        return JSONResponse(content={"sucesso": True, "message": "Histórico de conversa redefinido com sucesso."})
    return JSONResponse(content={"sucesso": False, "message": "Sessão não encontrada."}, status_code=404)

@app.get("/api/files")
async def list_files_endpoint():
    """
    Escanear recursivamente a pasta 'conversas/' e agrupar por sessão de conversa.
    """
    conversas_dir = "conversas"
    conversas_agrupadas = []
    
    if os.path.exists(conversas_dir):
        for session_id in os.listdir(conversas_dir):
            path_session = os.path.join(conversas_dir, session_id)
            if os.path.isdir(path_session):
                # Inicializa a conversa
                conversa = {
                    "session_id": session_id,
                    "titulo": session_id.replace("_", " ").title(),
                    "respostas": [],
                    "programas": []
                }
                
                # Escaneia respostas
                dir_respostas = os.path.join(path_session, "respostas")
                if os.path.exists(dir_respostas):
                    for f in os.listdir(dir_respostas):
                        path_f = os.path.join(dir_respostas, f)
                        if os.path.isfile(path_f):
                            stat = os.stat(path_f)
                            conversa["respostas"].append({
                                "name": f,
                                "size": stat.st_size,
                                "date": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
                            })
                            # Se for a primeira resposta, define o título a partir do slug do arquivo
                            if f.startswith("resposta_") and conversa["titulo"] == session_id.replace("_", " ").title():
                                slug_match = re.match(r"resposta_(.*)_\d{8}_\d{6}\.md", f)
                                if slug_match:
                                    slug = slug_match.group(1)
                                    conversa["titulo"] = slug.replace("_", " ").title()
                            
                # Escaneia programas
                dir_programas = os.path.join(path_session, "programas")
                if os.path.exists(dir_programas):
                    for f in os.listdir(dir_programas):
                        path_f = os.path.join(dir_programas, f)
                        if os.path.isfile(path_f):
                            stat = os.stat(path_f)
                            conversa["programas"].append({
                                "name": f,
                                "size": stat.st_size,
                                "date": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
                            })
                            
                # Ordena pelo mais recente
                conversa["respostas"].sort(key=lambda x: x["date"], reverse=True)
                conversa["programas"].sort(key=lambda x: x["date"], reverse=True)
                
                # Apenas inclui conversas que tenham ao menos uma resposta
                if conversa["respostas"]:
                    conversas_agrupadas.append(conversa)
    
    # Ordena as conversas pela data da resposta mais recente
    conversas_agrupadas.sort(key=lambda x: x["respostas"][0]["date"] if x["respostas"] else "", reverse=True)
    
    return JSONResponse(content={"conversas": conversas_agrupadas})

@app.get("/api/files/download/{session_id}/{tipo}/{filename}")
async def download_file_endpoint(session_id: str, tipo: str, filename: str):
    """
    Serve um arquivo de uma conversa específica para download ou visualização.
    tipo: 'respostas' ou 'programas'
    """
    if tipo not in ["respostas", "programas"]:
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido.")
        
    filepath = os.path.join("conversas", session_id, tipo, filename)
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
        
    return FileResponse(path=filepath, filename=filename, media_type="application/octet-stream")

# Cria a pasta de arquivos estáticos 'web/' se não existir
os.makedirs("web", exist_ok=True)

# Serve a pasta estática 'web/' na raiz '/'
app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Servidor Uvicorn da Interface Web Primordial...")
    uvicorn.run("web_server:app", host="127.0.0.1", port=8000, reload=True)
