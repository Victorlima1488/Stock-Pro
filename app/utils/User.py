from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from database.sqlite.connection import conexao_do_banco_teste
from sqlalchemy.orm import sessionmaker


# Configurando a conexão com o banco de dados SQLite usando SQLAlchemy
SQLALCHEMY_DATABASE_URL = conexao_do_banco_teste()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criando uma instância do declarative base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)
    address = Column(String)
    cpf = Column(String)
    gender = Column(String)
    age = Column(Integer)
    
# Criando todas as tabelas definidas com o SQLAlchemy
Base.metadata.create_all(bind=engine)