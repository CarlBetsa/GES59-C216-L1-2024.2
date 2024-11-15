from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__)

# URL base do backend
API_BASE_URL = "http://backend:8000"

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para exibir o formulário de cadastro (substituído por JSON)
@app.route('/cadastro', methods=['GET'])
def inserir_produto_form():
    return render_template('cadastro.html')

# Rota para enviar os dados do formulário de cadastro para a API
@app.route('/inserir', methods=['POST'])
def inserir_produto():
    nome = request.form['nome']
    quantidade = request.form['quantidade']
    preco = request.form['preco']

    payload = {
        'nome': nome,
        'quantidade' : quantidade,
        'preco' : preco
    }

    response = requests.post(f'{API_BASE_URL}/api/v1/produtos/', json=payload)
    
    if response.status_code == 201:
        return redirect(url_for('listar_produtos'))
    else:
        return "Erro ao inserir produto", 500

# Rota para listar todos os produtos
@app.route('/estoque', methods=['GET'])
def listar_produtos():
    response = requests.get(f'{API_BASE_URL}/api/v1/produtos/')
    try:
        produtos = response.json()
    except:
        produtos = []
    return render_template('estoque.html', produtos=produtos)

# Rota para exibir o formulário de edição de produto (substituído por JSON)
@app.route('/atualizar/<int:produto_id>', methods=['GET'])
def atualizar_produto_form(produto_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/produtos/{produto_id}")
    if response.status_code == 404:
        return jsonify({"error": "Produto não encontrado"}), 404
    produto = response.json()
    return render_template('atualizar.html', produto=produto)

# Rota para enviar os dados do formulário de edição de produto para a API
@app.route('/atualizar/<int:produto_id>', methods=['POST'])
def atualizar_produto(produto_id):
    nome = request.form['nome']
    quantidade = request.form['quantidade']
    preco = request.form['preco']

    payload = {
        'id': produto_id,
        'nome': nome,
        'quantidade' : quantidade,
        'preco' : preco
    }

    response = requests.patch(f"{API_BASE_URL}/api/v1/produtos/{produto_id}", json=payload)
    
    if response.status_code == 200:
        return redirect(url_for('listar_produtos'))
    else:
        return "Erro ao atualizar produto", 500

# Rota para exibir o formulário de venda de produto (substituído por JSON)
@app.route('/vender/<int:produto_id>', methods=['GET'])
def vender_produto_form(produto_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/produtos/")
    produtos = [produto for produto in response.json() if produto['id'] == produto_id]
    if len(produtos) == 0:
        return "Produto não encontrado", 404
    produto = produtos[0]
    return render_template('vender.html', produto=produto)

# Rota para vender um produto
@app.route('/vender/<int:produto_id>', methods=['POST'])
def vender_produto(produto_id):
    quantidade = request.form['quantidade']

    payload = {
        'quantidade': quantidade
    }

    response = requests.put(f"{API_BASE_URL}/api/v1/produtos/{produto_id}/vender/", json=payload)
    
    if response.status_code == 200:
        return redirect(url_for('listar_produtos'))
    else:
        return "Erro ao vender produto", 500

# Rota para listar todas as vendas
@app.route('/vendas', methods=['GET'])
def listar_vendas():
    response = requests.get(f"{API_BASE_URL}/api/v1/vendas/")
    try:
        vendas = response.json()
    except:
        vendas = []
    total_vendas = 0
    for venda in vendas:
        total_vendas += float(venda['valor_venda'])
    return render_template('vendas.html', vendas=vendas, total_vendas=total_vendas)

# Rota para excluir um produto
@app.route('/excluir/<int:produto_id>', methods=['POST'])
def excluir_produto(produto_id):
    response = requests.delete(f"{API_BASE_URL}/api/v1/produtos/{produto_id}")
    
    if response.status_code == 200:
        return redirect(url_for('listar_produtos'))
    else:
        return jsonify({"error": "Erro ao excluir produto"}), response.status_code

# Rota para resetar o banco de dados
@app.route('/reset-database', methods=['GET'])
def resetar_database():
    response = requests.delete(f"{API_BASE_URL}/api/v1/produtos/")
    
    if response.status_code == 200:
        return render_template('confirmacao.html')
    else:
        return jsonify({"error": "Erro ao resetar o banco de dados"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
