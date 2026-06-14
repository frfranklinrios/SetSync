from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

# Association table para membros da banda
band_members = db.Table(
    'band_members',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('band_id', db.String(36), db.ForeignKey('band.id'), primary_key=True),
    db.Column('role', db.String(20), default='member'),  # member, editor, admin, owner
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    owned_bands = db.relationship('Band', backref='owner', lazy=True, foreign_keys='Band.owner_id')
    bands = db.relationship('Band', secondary=band_members, backref=db.backref('members', lazy=True))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Band(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    cifras = db.relationship('Cifra', backref='band', lazy=True, cascade='all, delete-orphan')
    
    def is_member(self, user_id):
        return any(m.id == user_id for m in self.members)
    
    def is_admin(self, user_id):
        if self.owner_id == user_id:
            return True
        member = db.session.query(band_members).filter_by(
            user_id=user_id, band_id=self.id
        ).first()
        return member and member.role == 'admin' if member else False
    
    def get_role(self, user_id):
        if self.owner_id == user_id:
            return 'owner'
        member = db.session.query(band_members).filter_by(
            user_id=user_id, band_id=self.id
        ).first()
        return member.role if member else None

class Cifra(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = db.Column(db.String(200), nullable=False)
    artista = db.Column(db.String(200), nullable=False)
    tom_original = db.Column(db.String(10), default='C')  # Tom em que foi escrita
    conteudo = db.Column(db.Text, nullable=False)
    band_id = db.Column(db.String(36), db.ForeignKey('band.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
