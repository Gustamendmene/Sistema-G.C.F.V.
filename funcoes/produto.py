from banco.conexao import conectar

def inserir_produto(nome, categoria, marca, codigo_barras, fornecedor,
                    preco_custo, preco_venda, data_entrega, data_validade,
                    quantidade, quantidade_minima, lote, localizacao):
    """Cadastra o produto e já cria a linha dele no estoque."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            """INSERT INTO produto (nome, categoria, marca, codigo_barras, fornecedor,
               preco_custo, preco_venda, data_entrega, data_validade)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (nome, categoria, marca, codigo_barras, fornecedor,
             preco_custo, preco_venda, data_entrega, data_validade),
        )
        id_produto = cur.lastrowid
        cur.execute(
            """INSERT INTO estoque (id_produto, quantidade_atual, quantidade_minima,
               lote, localizacao) VALUES (%s,%s,%s,%s,%s)""",
            (id_produto, quantidade, quantidade_minima, lote, localizacao),
        )
        con.commit()
        return id_produto
    except Exception:
        con.rollback()   
        raise
    finally:
        cur.close()
        con.close()

def deletar_produto(id_produto):
    """Apaga o produto; o estoque dele some junto (ON DELETE CASCADE)."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
        con.commit()
        return cur.rowcount  
    finally:
        cur.close()
        con.close()

def listar_produtos():
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            """SELECT p.id_produto, p.nome, p.categoria, p.data_validade,
                      e.quantidade_atual, e.localizacao
               FROM produto p JOIN estoque e ON e.id_produto = p.id_produto
               ORDER BY p.nome"""
        )
        return cur.fetchall()
    finally:
        cur.close()
        con.close()