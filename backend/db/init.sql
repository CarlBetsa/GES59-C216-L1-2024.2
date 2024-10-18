DROP TABLE IF EXISTS "vendas";
DROP TABLE IF EXISTS "produtos";

CREATE TABLE "produtos" (
    "id" SERIAL PRIMARY KEY,
    "nome" VARCHAR(255) NOT NULL,
    "quantidade" INTEGER NOT NULL,
    "preco" FLOAT NOT NULL
);

CREATE TABLE "vendas" (
    "id" SERIAL PRIMARY KEY,
    "produto_id" INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    "quantidade_vendida" INTEGER NOT NULL,
    "valor_venda" FLOAT NOT NULL,
    "data_venda" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserindo alguns produtos de exemplo
INSERT INTO "produtos" ("nome", "quantidade", "preco") 
VALUES ('Mesa 6 lugares', 6, 430.00), ('Cadeira', 40, 50.00), ('Sofa', 3, 700.00);
