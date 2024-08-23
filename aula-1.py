def cadastrar_produto(estoque):
    nome = input("Digite o nome do produto: ")
    quantidade = int(input("Digite a quantidade do produto: "))
    preco = float(input("Digite o preço do produto: "))
    
    estoque.append({'nome': nome, 'quantidade': quantidade, 'preco': preco})
    print("Produto cadastrado com sucesso!")

def listar_produtos(estoque):
    if not estoque:
        print("O estoque está vazio.")
    else:
        print("Produtos em estoque:")
        for produtos in estoque:
            print(f"Nome: {produtos['nome']}, Quantidade: {produtos['quantidade']}, Preço: R${produtos['preco']:.2f}")

def consultar_produto(estoque):
    nome = input("Digite o nome do produto que deseja consultar: ")
    for produto in estoque:
        if produto["nome"] == nome:
            print(f"Nome: {produto['nome']}, Quantidade: {produto['quantidade']}, Preço: R${produto['preco']:.2f}")
            return
    print("Produto não encontrado no sistema.")

def vender_produto(estoque):
    nome = input("Digite o nome do produto vendido: ")
    for produto in estoque:
        if produto["nome"] == nome:
            quantidade_venda = int(input("Digite a quantidade vendida: "))
            if produto["quantidade"] >= quantidade_venda:
                produto["quantidade"] -= quantidade_venda
                print(f"{quantidade_venda} unidade(s) de {produto['nome']} vendida(s) com sucesso!")
                return
            else: 
                print("Quantidade insuficiente no estoque.")
                return

    print("Produto não encontrado no sistema.")

def menu():
    estoque = []
    while True:
        print("\nSistema de Gerenciamento de Estoque")
        print("1. Cadastrar Produto")
        print("2. Listar Produtos")
        print("3. Consultar Produto")
        print("4. Vender Produto")
        print("5. Sair")
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_produto(estoque)
        elif opcao == "2":
            listar_produtos(estoque)
        elif opcao == "3":
            consultar_produto(estoque)
        elif opcao == "4":
            vender_produto(estoque)
        elif opcao == "5":
            print("Saindo do sistema.")
            break
        else:
            print("Opção inválida! Por favor, tente novamente.")


menu()
