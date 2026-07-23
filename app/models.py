from app import db
from datetime import datetime, timezone, timedelta, date

class favoritos(db.Model):
    __tablename__ = 'favoritos'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    usuario_id = db.Column(db.Integer)
    produto_id = db.Column(db.Integer)

class produtos(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100))
    descricao = db.Column(db.String(500))
    imagem = db.Column(db.String(130))
    preco = db.Column(db.Numeric(precision=6, scale=2))
    marca = db.Column(db.String(50))

class registros(db.Model):
    __tablename__ = 'registros'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(5000))
    senha = db.Column(db.String(5000))
    blind_index = db.Column(db.String(5000))
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class registros_temporarios(db.Model):
    __tablename__ = 'registros_temporarios'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String)
    codigo = db.Column(db.String(1000))
    horario = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    senha = db.Column(db.String)
    blind_index = db.Column(db.String(5000))
    nome = db.Column(db.String(100))

class RefreshTokens(db.Model):
    __tablename__ = 'RefreshTokens'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    token = db.Column(db.String(500))
    userid = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expired_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(days=7))

class user_profile(db.Model):
    __tablename__ = 'user_profile'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome_completo = db.Column(db.String(100))
    primeiro_nome = db.Column(db.String(200))
    foto_url = db.Column(db.String(130))
    bio = db.Column(db.String(50))
    data_de_nascimento = db.Column(db.Date, default=date(2000, 1, 1))
    vendedor = db.Column(db.Boolean, default=False)
    nivel = db.Column(db.Numeric(precision=4, scale=2))
    compras = db.Column(db.Integer)
    user_id = db.Column(db.Integer)