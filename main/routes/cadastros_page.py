import sqlalchemy
import streamlit as st
from src.utils.email import EmailSender
from src.models.repository.product_repository import ProductRepository
from src.models.repository.user_repository import UserRepository
from src.utils.uteis import Logger, str_as_number, validate_email
from src.models.configs.config_geral import configs
from src.models.repository.dataframes_repository import (
    select_all_clientes,
    select_all_products,
)


def alter_client(cliente, nome=None, cpf=None, email=None, telefone=None):
    """Altera os dados do cliente no banco de dados

    Args:
        cliente (str): username do cliente a alterar
        nome (str, optional): nome. Defaults to None.
        cpf (str, optional): cpf. Defaults to None.
        email (str, optional): email. Defaults to None.
        telefone (str/int, optional): numero de telefone. Defaults to None.
    """
    with UserRepository() as u:
        try:
            cliente_u = u.select_user(cliente, "Cliente")
            if not cliente_u:
                st.error("Usuário não encontrado")
            else:
                if nome:
                    cliente_u.nome = nome
                    Logger.info(f"setting nome for {nome}")
                if cpf:
                    str_as_number(cpf)
                    cliente_u.cpf = cpf
                    Logger.info(f"setting cpf for {cpf}")
                if email:
                    cliente_u.email = email
                    Logger.info(f"setting email for {email}")
                if telefone:
                    str_as_number(telefone)
                    cliente_u.telefone = telefone
                    Logger.info(f"setting telefone for {telefone}")
                u.session.add(cliente_u)
                u.session.commit()
                st.success("Cliente alterado com sucesso")
        except sqlalchemy.exc.IntegrityError as e:
            Logger.error(f"Erro ao alterar dados do cliente: {e}")
            st.error("Este email ou CPF já existe em um cadastro!!!")
            st.warning("Tente novamente com dados diferentes!!!")
        except Exception as e:
            Logger.error(str(e))
            st.error("Erro ao cadastrar o cliente")


def register_client(nome: str, cpf: str, telefone: str, email: str):
    """Registra um novo cliente no banco de dados

    Args:
        nome (str): nome
        cpf (str): cpf
        telefone (str/int): telefone
        email (str): email
    """
    try:
        cpf = str_as_number(cpf)
        telefone = str_as_number(telefone)

        cadasto = UserRepository().insert_user(
            username=nome,
            cpf=cpf,
            telefone=telefone,
            email=email,
            type_user="Cliente",
        )
        if cadasto:
            st.success(f"Cliente {nome} cadastrado com sucesso!")
        else:
            st.error("Não foi possivel cadastrar o cliente")
    except sqlalchemy.exc.IntegrityError as e:
        Logger.error(f"Erro ao alterar dados do cliente: {e}")
        st.error("Este email ou CPF já existe em um cadastro!!!")
        st.warning("Tente novamente com dados diferentes!!!")
    except Exception as e:
        Logger.error(str(e))
        st.error("Erro ao alterar dados do cliente!!")


def alter_product(produto, nome=None, preco=None, qtde=None, categoria=None):
    """Altera o produtos no banco de dados

    Args:
        produto (str): nome do produto a alterar
        nome (str, optional): nome. Defaults to None.
        preco (float/int, optional): preco. Defaults to None.
        qtde (int, optional): quantidade. Defaults to None.
        categoria (str, optional): categoria. Defaults to None.
    """
    with ProductRepository() as p:
        try:
            produto_u = p.select_product(produto)
            if not produto_u:
                st.error("Produto não encontrado")
            else:
                if nome:
                    produto_u.nome = nome
                if preco:
                    produto_u.preco = preco
                if qtde:
                    produto_u.qtde = qtde
                if categoria:
                    produto_u.categoria = categoria
                p.session.add(produto_u)
                p.session.commit()
                st.success("Produto alterado com sucesso")
        except Exception as e:
            Logger.error(str(e))
            st.error("Erro ao cadastrar o produto")


def register_product(nome, preco, qtde, categoria):
    try:
        ProductRepository().insert_product(nome, float(preco), int(qtde), categoria)
        st.success(f"Produto {nome} cadastrado com sucesso!")
    except Exception as e:
        Logger.error(str(e))
        st.error("Erro ao cadastrar o produto")


# Função para o cadastro de produtos
def cadastro_produto():
    """Pagina para cadastro de produtos"""
    st.html(
        "<h1 style='font-size:33px;color:darkgray;'><span style='color:#DAA520'>Cadastro(s)</span> e <span style='color:#8B4513'>Deleção(es)</span> de Produtos<h1/>"
    )
    selection = st.selectbox(
        "**:green[Selecione a ação]**", ["Cadastro", "Deleção", "Alterar"]
    )
    if selection == "Cadastro":
        nome = st.text_input(":green[Nome do Produto]")
        preco = st.number_input(":green[Preço]", min_value=0.0, step=0.01)
        qtde = st.number_input(":green[Quantidade]", min_value=0, step=1)
        categoria = st.selectbox(
            ":green[Selecione uma da(s) categoria(s)]",
            ["categoria", "Bebidas", "Doces", "Salgados", "Padaria", "Mercearia"],
        )
        flag = (
            True
            if not nome
            or not preco
            or not qtde
            or not categoria
            or categoria == "categoria"
            else False
        )
        if flag:
            st.warning("Todos os campos são obrigatorios!!")
        if st.button(
            "Cadastrar Produto",
            type="primary",
        ):
            if flag:
                st.error("Todos os campos são obrigatorios!! Por favor preencha todos")
            else:
                register_product(nome, preco, qtde, categoria)
    elif selection == "Alterar":
        produto = st.selectbox(
            "**:green[Selecione o produto]**",
            select_all_products(),
            help="selecione o produto que deseja alterar",
        )
        nome = st.text_input(":orange[Novo Nome do Produto]")
        preco = st.number_input(":orange[Novo Preço]", min_value=0.0, step=0.01)
        qtde = st.number_input(
            ":orange[Nova Quantidade em estoque]", min_value=0, step=1
        )
        categoria = st.selectbox(
            ":orange[Selecione uma da(s) categoria(s)]",
            ["categoria", "Bebidas", "Doces", "Salgados", "Padaria", "Mercearia"],
        )
        if st.button("Alterar", type="primary"):
            alter_product(produto, nome, preco, qtde, categoria)
    else:
        produto = st.selectbox(":red[Selecione o produto]", select_all_products())
        Logger.info(f">>> Produto selecionado: {produto}")
        if st.button("Deletar Produto", type="primary"):
            deletion = ProductRepository().delete_product(produto)
            if deletion:
                st.success(f"Produto {produto} deletado com sucesso!")
            else:
                st.error("Não foi possivel apagar o produto")
    if st.sidebar.button(
        "ir para home",
        use_container_width=True,
        type="primary",
    ):
        st.session_state["pagina"] = "homepage"
        st.rerun()


def cadastro_cliente():
    """Pagina para cadastro de clientes"""
    st.html(
        "<h1 style='font-size:33px;color:darkgray;'><span style='color:#DAA520'>Cadastro(s)</span> e <span style='color:#8B4513'>Deleção(es)</span> de Clientes<h1/>"
    )
    action = st.selectbox(
        "**:green[Selecione a ação]**",
        ["Cadastro", "Deleção", "Alterar"],
        help="Selecione a ação que deseja realizar",
    )
    if action == "Cadastro":
        nome = st.text_input("Nome do Cliente")
        cpf = st.text_input(
            "CPF do Cliente", placeholder="666.666.666-69", max_chars=14
        )
        email = st.text_input("Email do Cliente", placeholder="marcosmendes@gmail.com")
        telefone = st.text_input(
            "Telefone do Cliente", placeholder="(21) 77070-7070", max_chars=15
        )
        flag = True if not cpf or not email or not nome or not telefone else False
        if flag:
            st.warning("Todos os campos são obrigatorios!!")

        if st.button("Cadastrar Cliente", type="primary"):
            if flag:
                st.error("Todos os campos são obrigatorios!! Por favor preencha todos")
            else:
                if validate_email(email):
                    register_client(nome, cpf, telefone, email)
                else:
                    st.error("Email invalido")
    elif action == "Alterar":
        cliente = st.selectbox(
            "**:orange[Selecione o cliente]**",
            select_all_clientes(),
            help="selecione o cliente que deseja alterar",
        )
        nome = st.text_input("Novo Nome do Cliente")
        cpf = st.text_input("Novo CPF do Cliente", placeholder="666.666.666-69")
        email = st.text_input(
            "Novo Email do Cliente", placeholder="marcosmendes@gmail.com"
        )
        telefone = st.text_input(
            "Novo Telefone do Cliente", placeholder="(21) 77070-7070"
        )
        if st.button("Alterar", type="primary"):
            if not email:
                alter_client(cliente, nome, cpf, email, telefone)
            elif email:
                if validate_email(email):
                    alter_client(cliente, nome, cpf, email, telefone)
                else:
                    st.error("Email invalido")
    else:
        cliente = st.selectbox(":red[Selecione o cliente]", select_all_clientes())
        if st.button("Deletar Cliente", type="primary"):
            Logger.info(f">>> Cliente á deletar: {cliente}")
            deletion = UserRepository().delete_user(cliente, "Cliente")
            if deletion:
                st.success(f"Cliente {cliente} deletado com sucesso!")
            else:
                st.error("Não foi possivel apagar o cliente")
        st.warning("Atenção, essa ação é irreversível!!!")
    if st.sidebar.button("ir para home", use_container_width=True, type="primary"):
        st.session_state["pagina"] = "homepage"
        st.rerun()


def customer_registration():
    """Pagina para registo de clientes para clientes"""
    st.html(
        "<h1 style='font-size:33px;color:darkgray;'><span style='color:#DAA520'>Cadastro(s)</span></span> de Clientes, <span style='color:#DAA520'>Registre-se</span><h1/>"
    )
    nome = st.text_input("Nome completo:", placeholder="Marcos Mendes")
    cpf = st.text_input("CPF:", placeholder="666.666.666-69", max_chars=14)
    senha = st.text_input("Senha:", type="password")
    telefone = st.text_input("Telefone:", placeholder="(21) 77070-7070", max_chars=15)
    email = st.text_input("Email:", placeholder="marcosmendes@gmail.com")
    cpf = str_as_number(cpf)
    telefone = str_as_number(telefone)
    if st.button("Cadastrar", type="primary"):
        if not validate_email(email):
            st.error("Email invalido")
        if not nome or not cpf or not senha or not telefone or not email:
            st.warning("Todos os campos são obrigatorios!!")
        else:
            if UserRepository().insert_user(
                nome, senha, cpf, telefone, email, "Cliente"
            ):
                email_sender = EmailSender()
                message = f"""<html>
    <p>Olá <b>{nome}</b>, seja bem-vindo ao nosso sistema!</p>
    <p>Você se cadastrou com sucesso e agora pode aproveitar todos os nossos serviços.</p>
    <p><b>Seus dados de acesso:</b><br>
    Login: {email}<br>
    Senha: {senha}</p>
    <p>Caso tenha alguma dúvida ou precise de ajuda, não hesite em entrar em contato conosco.</p>
    <p>Agradecemos por escolher nosso serviço!</p>
    <p>Atenciosamente,<br>
    Equipe de Suporte Padaria da Vila.</p>
    </html>"""
                email_sender.send_email(
                    email, message, subject="Seja bem-vindo ao nosso sistema"
                )
                email_sender.send_email(
                    configs["user"],
                    message,
                    subject="Novo cliente registrou-se em nosso sistema",
                )
                st.success(f"Cadastrado efetuado {nome}, retorne ao login!")
            else:
                st.error("Erro ao cadastrar o cliente")
    if st.sidebar.button("Voltar", use_container_width=True, type="primary"):
        st.session_state["pagina"] = "homepage"
        st.rerun()
