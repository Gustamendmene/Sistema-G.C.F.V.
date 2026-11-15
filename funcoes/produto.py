"""CRUD de produtos (acesso ao banco). Nada aqui conhece a interface."""
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


def buscar_produto(id_produto):
    """Dados completos de um produto (dict) ou None se não existir."""
    con = conectar()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute(
            """SELECT p.id_produto, p.nome, p.categoria, p.marca,
                      p.codigo_barras, p.fornecedor, p.preco_custo,
                      p.preco_venda, p.data_entrega, p.data_validade,
                      e.quantidade_atual, e.quantidade_minima,
                      e.lote, e.localizacao
               FROM produto p JOIN estoque e ON e.id_produto = p.id_produto
               WHERE p.id_produto = %s""",
            (id_produto,),
        )
        return cur.fetchone()
    finally:
        cur.close()
        con.close()


def atualizar_produto(id_produto, nome, categoria, marca, codigo_barras,
                      fornecedor, preco_custo, preco_venda, data_entrega,
                      data_validade, quantidade, quantidade_minima, lote,
                      localizacao):
    """Atualiza produto e estoque na mesma transação.

    Devolve True se o produto existia e False se não foi encontrado.
    (Não usamos rowcount: o MySQL devolve 0 quando os valores novos são
    iguais aos antigos, o que pareceria "não encontrado".)
    """
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT 1 FROM produto WHERE id_produto = %s FOR UPDATE",
            (id_produto,),
        )
        if cur.fetchone() is None:
            con.rollback()
            return False

        cur.execute(
            """UPDATE produto SET nome=%s, categoria=%s, marca=%s,
               codigo_barras=%s, fornecedor=%s, preco_custo=%s,
               preco_venda=%s, data_entrega=%s, data_validade=%s
               WHERE id_produto=%s""",
            (nome, categoria, marca, codigo_barras, fornecedor,
             preco_custo, preco_venda, data_entrega, data_validade,
             id_produto),
        )
        cur.execute(
            """UPDATE estoque SET quantidade_atual=%s, quantidade_minima=%s,
               lote=%s, localizacao=%s WHERE id_produto=%s""",
            (quantidade, quantidade_minima, lote, localizacao, id_produto),
        )
        con.commit()
        return True
    except Exception:
        con.rollback()
        raise
    finally:
        cur.close()
        con.close()


def deletar_produto(id_produto):
    """Apaga o produto; o estoque dele some junto (ON DELETE CASCADE).

    Devolve quantas linhas de produto foram apagadas (0 = já não existia).
    """
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
        con.commit()
        return cur.rowcount
    except Exception:
        con.rollback()
        raise
    finally:
        cur.close()
        con.close()


def listar_produtos():
    """Lista para a tabela da tela (cada linha é um dict)."""
    con = conectar()
    cur = con.cursor(dictionary=True)
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
