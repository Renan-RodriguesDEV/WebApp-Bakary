import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    TIMESTAMP,
    ForeignKey,
    DECIMAL,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from src.utils.uteis import Logger


class DatabaseHandler:

    def __init__(
        self, user="root", password="", host="localhost", database="db_comercio"
    ):
        __user = user
        __password = password
        __host = host
        __database = database
        self.__str_url = f"mysql+pymysql://{__user}:{__password}@{__host}/{__database}"
        self.__engine = create_engine(self.__str_url)
        self.session = None

    def get_engine(self):
        return self.__engine

    def __enter__(self):
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


Base = declarative_base()


class Produto(Base):
    __tablename__ = "produtos"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(255), nullable=False)
    preco = Column("preco", DECIMAL(15, 2), nullable=False)
    estoque = Column("estoque", Integer, nullable=False)

    def __init__(self, nome, preco, estoque):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(255))
    cpf = Column("cpf", String(11), nullable=True, unique=True)
    telefone = Column("telefone", String(15), nullable=True)
    email = Column("email", String(255), nullable=True)

    def __init__(self, nome, cpf=None, telefone=None, email=None):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email


class User(Base):
    __tablename__ = "users"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(255), nullable=False)
    senha = Column("senha", String(13), nullable=True, unique=True)

    def __init__(self, nome, senha=None):
        self.nome = nome
        self.senha = senha


class Cliente_Produto(Base):
    __tablename__ = "cliente_produto"
    id = Column(
        "id", Integer, primary_key=True, autoincrement=True
    )  # Adiciona chave primária
    id_cliente = Column("id_cliente", ForeignKey("clientes.id"), nullable=False)
    id_produto = Column("id_produto", ForeignKey("produtos.id"), nullable=False)
    preco = Column("preco", DECIMAL(15, 2))
    quantidade = Column(
        "quantidade",
        Integer,
    )
    total = Column("total", DECIMAL(15, 2))
    data = Column("data", TIMESTAMP, server_default=func.now())


class Divida(Base):
    __tablename__ = "dividas"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    id_cliente = Column("id_cliente", ForeignKey("clientes.id"), nullable=False)
    valor = Column("valor", DECIMAL(15, 2), nullable=False)
    pago = Column("pago", DECIMAL(15, 2), nullable=False, default=0)
    data_modificacao = Column("data_modificacao", TIMESTAMP, server_default=func.now())

    def __init__(self, cliente, valor):
        self.id_cliente = cliente.id
        self.valor = valor
        self.data_modificacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def initialize_database():
    with DatabaseHandler() as database_handler:
        # Criação das tabelas no banco de dados
        Base.metadata.create_all(database_handler.get_engine())
        Logger.log_green("[INFO] - Initialization database sucessfully - [INFO]")
        result = (
            database_handler.session.query(User)
            .filter_by(nome="root")
            .filter_by(senha="superuser")
            .first()
        )
        if not result:
            user = User("root", "superuser")
            database_handler.session.add(user)
            database_handler.session.commit()
            Logger.log_blue(f"[INFO] User {user.nome} added successfully [INFO]")
