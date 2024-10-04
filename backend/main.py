from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time

# Inicializar o repositório de produtos
produtos = [
    {"id": 1, "nome": "Produto A", "quantidade": 10, "preco": 50.0},
    {"id": 2, "nome": "Produto B", "quantidade": 5, "preco": 40.0},
]

# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para cadastrar novos produtos
class Produto(BaseModel):
    id: Optional[int] = None
    nome: str
    quantidade: int
    preco: float

# Modelo para venda de produto
class VendaProduto(BaseModel):
    quantidade: int

# Modelo para atualizar atributos de um produto
class AtualizarProduto(BaseModel):
    nome: Optional[str] = None
    quantidade: Optional[int] = None
    preco: Optional[float] = None

# Função para gerar o próximo ID dinamicamente
def gerar_proximo_id():
    if produtos:
        return max(produto['id'] for produto in produtos) + 1
    else:
        return 1

# Função auxiliar para buscar produto por ID
def buscar_produto_por_id(produto_id: int):
    for produto in produtos:
        if produto["id"] == produto_id:
            return produto
    return None

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

# 1. Cadastrar um novo produto
@app.post("/api/v1/produtos/", status_code=201)
def cadastrar_produto(produto: Produto):
    for p in produtos:
        if  p["nome"].lower() == produto.nome.lower():
            raise HTTPException(status_code=400, detail="Produto já existe.")
        
    # Gerar ID dinamicamente
    novo_produto = produto.dict()
    novo_produto['id'] = gerar_proximo_id()

    # Adicionar o novo produto ao repositório
    produtos.append(novo_produto)
    return {"message": "Produto cadastrado com sucesso!", "produto": novo_produto}

# 2. Listar todos os produtos
@app.get("/api/v1/produtos/", response_model=List[Produto])
def listar_produtos():
    if not produtos:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado.")
    return produtos

# 3. Consultar produto por ID
@app.get("/api/v1/produtos/{produto_id}")
def consultar_produto(produto_id: int):
    produto = buscar_produto_por_id(produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return produto

# 4. Vender um produto (reduzir quantidade no estoque)
@app.put("/api/v1/produtos/{produto_id}/vender/")
def vender_produto(produto_id: int, venda: VendaProduto):
    produto = buscar_produto_por_id(produto_id)
    
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    
    if produto["quantidade"] < venda.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente no estoque.")
    
    produto["quantidade"] -= venda.quantidade
    return {"message": "Venda realizada com sucesso!", "produto": produto}

# 5. Atualizar atributos de um produto (nome, quantidade, preço)
@app.patch("/api/v1/produtos/{produto_id}")
def atualizar_produto(produto_id: int, produto_atualizacao: AtualizarProduto):
    produto = buscar_produto_por_id(produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    
    # Atualizar apenas os campos fornecidos
    if produto_atualizacao.nome is not None:
        produto["nome"] = produto_atualizacao.nome
    if produto_atualizacao.quantidade is not None:
        produto["quantidade"] = produto_atualizacao.quantidade
    if produto_atualizacao.preco is not None:
        produto["preco"] = produto_atualizacao.preco

    return {"message": "Produto atualizado com sucesso!", "produto": produto}

# 6. Remover um produto por ID
@app.delete("/api/v1/produtos/{produto_id}")
def remover_produto(produto_id: int):
    for i, produto in enumerate(produtos):
        if produto["id"] == produto_id:
            del produtos[i]
            return {"message": "Produto removido com sucesso!"}
    
    raise HTTPException(status_code=404, detail="Produto não encontrado.")

# 7. Resetar o estoque (remover todos os produtos)
@app.delete("/api/v1/produtos/")
def resetar_estoque():
    global produtos
    produtos = [
        {"id": 1, "nome": "Produto A", "quantidade": 10, "preco": 50.0},
        {"id": 2, "nome": "Produto B", "quantidade": 5, "preco": 40.0},
    ]
    return {"message": "Estoque resetado com sucesso!"}
