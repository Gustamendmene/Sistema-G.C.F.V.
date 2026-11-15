# Sistema G.C.F.V. — Mercadinho São José

Sistema de controle de estoque e validade, feito em Python com Flet e MySQL.

## Como executar (Windows)

1. Abra a pasta do projeto no VS Code (File > Open Folder).
2. Abra o terminal e crie o ambiente virtual: `python -m venv .venv`
3. Ative: `.\.venv\Scripts\Activate.ps1`
4. Instale as dependências: `python -m pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e coloque a sua senha do MySQL.
6. Execute **sempre pelo main**: `python main.py`

## Estrutura

```
main.py          ponto de entrada: menu lateral e navegação entre telas
tema.py          cores usadas em todo o sistema
banco/           conexão com o MySQL (lê o .env)
funcoes/         produto.py (CRUD), estoque.py (consultas), alertas.py (regras dos alertas)
telas/           uma tela por arquivo (inicio, produtos, lotes, estoque, validade)
componentes/     peças reutilizáveis: ui.py (tabelas, cartões), alertas_ui.py (sino/painel), listagem.py
utils/           datas.py, validacao.py (formulário) e erros.py (log + mensagens)
logs/            erros.log (criado sozinho; fica fora do GitHub)
```

## Onde procurar quando algo der errado

| Sintoma | Onde olhar |
|---|---|
| Mensagem vermelha na tela | O texto já explica; o detalhe técnico está em `logs/erros.log` |
| Erro de senha/conexão | Arquivo `.env` (veja `.env.example`) |
| Dado salvo errado ou erro de SQL | `funcoes/` |
| Campo rejeitado indevidamente | `utils/validacao.py` |
| Visual / botão | `telas/` e `componentes/ui.py` |

## Como criar uma nova tela

1. Crie `telas/minha_tela.py` com a função `criar_tela(page, navegar)`.
2. Registre em `TELAS` e no menu, dentro do `main.py`.

## Alertas

Os alertas vêm da view `alerta_estoque` do MySQL e são tratados em `funcoes/alertas.py`.

| Alerta | Quando | Cor |
|---|---|---|
| VENCIDO | validade já passou | vermelho |
| VENCE HOJE / URGENTE | vence em até 3 dias (`DIAS_URGENTE`) | vermelho |
| A VENCER | vence em até 7 dias | amarelo |
| ESTOQUE BAIXO | quantidade atual <= mínima | laranja |

Onde aparecem: sino com contador em todas as telas (clique abre o painel), caixa
"Alertas em destaque" no Início, aviso ao abrir o sistema (se houver vencido ou
urgente) e a tela Validade, com filtros por tipo. O contador usa um cache de 30 s e
é atualizado na hora ao cadastrar, editar ou excluir produtos.
