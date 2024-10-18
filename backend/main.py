from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

# Função para obter a conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/produtos") 
    return await asyncpg.connect(DATABASE_URL)

# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para cadastrar novos produtos
class Produto(BaseModel):
    id: Optional[int] = None
    nome: str
    quantidade: int
    preco: float

class ProdutoBase(BaseModel):
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

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

# Função para verificar se o produto existe
async def produto_existe(nome: str, conn: asyncpg.Connection):
    try:
        query = "SELECT * FROM produtos WHERE LOWER(nome) = LOWER($1)"
        result = await conn.fetchval(query, nome)
        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao verificar se o produto existe: {str(e)}")
    

# 1. Cadastrar um novo produto
@app.post("/api/v1/produtos/", status_code=201)
async def cadastrar_produto(produto: ProdutoBase):
    conn = await get_database()
    if await produto_existe(produto.nome, conn):
        raise HTTPException(status_code=400, detail="Produto já existe.")
    
    try:
        query = "INSERT INTO produtos (nome, quantidade, preco) VALUES ($1, $2, $3)"
        async with conn.transaction():
            result = await conn.execute(query, produto.nome, produto.quantidade, produto.preco)
            return {"message": "Produto cadastrado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao cadastrar o produto: {str(e)}")
    finally:
        await conn.close()  

# 2. Listar todos os produtos
@app.get("/api/v1/produtos/", response_model=List[Produto])
async def listar_produtos():
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos"
        rows = await conn.fetch(query)
        produtos = [dict(row) for row in rows]
        return produtos
    finally:
        await conn.close()

# 3. Consultar produto por ID
@app.get("/api/v1/produtos/{produto_id}")
async def consultar_produto(produto_id: int):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")
        return dict(produto)
    finally:
        await conn.close()

# 4. Vender um produto (reduzir quantidade no estoque)
@app.put("/api/v1/produtos/{produto_id}/vender/")
async def vender_produto(produto_id: int, venda: VendaProduto):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        if produto['quantidade'] < venda.quantidade:
            raise HTTPException(status_code=400, detail="Quantidade insuficiente no estoque.")

        nova_quantidade = produto['quantidade'] - venda.quantidade
        update_query = "UPDATE produtos SET quantidade = $1 WHERE id = $2"
        await conn.execute(update_query, nova_quantidade, produto_id)

        valor_venda = produto['preco'] * venda.quantidade
        insert_venda_query = """
            INSERT INTO vendas (produto_id, quantidade_vendida, valor_venda) 
            VALUES ($1, $2, $3)
        """
        await conn.execute(insert_venda_query, produto_id, venda.quantidade, valor_venda)

        produto_atualizado = dict(produto)
        produto_atualizado['quantidade'] = nova_quantidade

        return {"message": "Venda realizada com sucesso!", "produto": produto_atualizado}
    finally:
        await conn.close()

# 5. Atualizar atributos de um produto
@app.patch("/api/v1/produtos/{produto_id}")
async def atualizar_produto(produto_id: int, produto_atualizacao: AtualizarProduto):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        update_query = """
            UPDATE produtos
            SET nome = COALESCE($1, nome),
                quantidade = COALESCE($2, quantidade),
                preco = COALESCE($3, preco)
            WHERE id = $4
        """
        await conn.execute(
            update_query,
            produto_atualizacao.nome,
            produto_atualizacao.quantidade,
            produto_atualizacao.preco,
            produto_id
        )
        return {"message": "Produto atualizado com sucesso!"}
    finally:
        await conn.close()

# 6. Remover um produto por ID
@app.delete("/api/v1/produtos/{produto_id}")
async def remover_produto(produto_id: int):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        delete_query = "DELETE FROM produtos WHERE id = $1"
        await conn.execute(delete_query, produto_id)
        return {"message": "Produto removido com sucesso!"}
    finally:
        await conn.close()

# 7. Resetar o estoque (remover todos os produtos)
@app.delete("/api/v1/produtos/")
async def resetar_estoque():
    init_sql = os.getenv("INIT_SQL", "db/init.sql")
    conn = await get_database()
    try:
        with open(init_sql, 'r') as file:
            sql_commands = file.read()
        await conn.execute(sql_commands)
        return {"message": "Estoque resetado com sucesso!"}
    finally:
        await conn.close()

# 8. Listar vendas
@app.get("/api/v1/vendas/")
async def listar_vendas():
    conn = await get_database()
    try:
        query = "SELECT * FROM vendas"
        rows = await conn.fetch(query)
        vendas = [dict(row) for row in rows]
        return vendas
    finally:
        await conn.close()
