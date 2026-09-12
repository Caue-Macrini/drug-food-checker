import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

def now():
    return datetime.now(timezone.utc).isoformat()

class Base(DeclarativeBase):
    pass

engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///./drugfood.db'), **({'connect_args': {'check_same_thread': False}} if os.getenv('DATABASE_URL', 'sqlite:').startswith('sqlite:') else {}))
Session = sessionmaker(engine, expire_on_commit=False)

class User(Base):
    __tablename__ = 'usuarios'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default='user')
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    token_version: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(String(40), default=now)

class Profile(Base):
    __tablename__ = 'perfis_clinicos'
    user_id: Mapped[str] = mapped_column(ForeignKey('usuarios.id'), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)

class Consent(Base):
    __tablename__ = 'consentimentos'
    user_id: Mapped[str] = mapped_column(ForeignKey('usuarios.id'), primary_key=True)
    version: Mapped[str] = mapped_column(String(30), default='1.0')
    accepted_at: Mapped[str] = mapped_column(String(40), default=now)

class HistoryKey(Base):
    __tablename__ = 'chaves_historico'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('usuarios.id'), index=True)
    month: Mapped[str] = mapped_column(String(7))

class History(Base):
    __tablename__ = 'historico_consultas'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_key: Mapped[str] = mapped_column(ForeignKey('chaves_historico.id'), index=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now, index=True)
    result: Mapped[dict] = mapped_column(JSON)

class Audit(Base):
    __tablename__ = 'logs_auditoria'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[str] = mapped_column(String(40), default=now)

class Reset(Base):
    __tablename__ = 'recuperacao_senha'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('usuarios.id'), index=True)
    expires: Mapped[int] = mapped_column(Integer)

class Dataset(Base):
    __tablename__ = 'versoes_base'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[str] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(500))
    count: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now)

class Drug(Base):
    __tablename__ = 'medicamentos'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    flags: Mapped[dict] = mapped_column(JSON, default=dict)

class Food(Base):
    __tablename__ = 'alimentos'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)

class Interaction(Base):
    __tablename__ = 'interacoes'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    drug_id: Mapped[str] = mapped_column(ForeignKey('medicamentos.id'))
    food_id: Mapped[str] = mapped_column(ForeignKey('alimentos.id'))
    dataset_id: Mapped[str] = mapped_column(ForeignKey('versoes_base.id'))
    data: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (Index('ix_interacao_par', 'drug_id', 'food_id', 'dataset_id'),)
