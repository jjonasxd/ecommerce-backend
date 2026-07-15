from app import db
from datetime import datetime, timezone

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

class registros_temporarios(db.Model):
    __tablename__ = 'registros_temporarios'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String)
    codigo = db.Column(db.String(1000))
    horario = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    senha = db.Column(db.String)
    blind_index = db.Column(db.String(5000))
    nome = db.Column(db.String(100))
