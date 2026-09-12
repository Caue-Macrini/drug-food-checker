"""Create an administrator without a default password: python manage.py create-admin."""
import argparse, getpass
import bcrypt
from sqlalchemy import select
from models import Base, engine, Session, User, Profile, Consent
from schemas import Signup
from services import uid

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['create-admin'])
    parser.parse_args()
    data = Signup(name=input('Nome: '), email=input('E-mail: '), password=getpass.getpass('Senha (mínimo 10 caracteres): '), consent=True)
    if input('Aceita o termo de tratamento do perfil para personalização, versão 1.0? [s/N]: ').lower() != 's':
        raise SystemExit('Cadastro cancelado')
    Base.metadata.create_all(engine)
    with Session() as db:
        if db.scalar(select(User).where(User.email == data.email)):
            raise SystemExit('E-mail já cadastrado')
        user = User(id=uid(), name=data.name, email=data.email, password=bcrypt.hashpw(data.password.encode(),bcrypt.gensalt(12)).decode(),role='admin')
        db.add(user)
        db.flush()
        db.add_all([Profile(user_id=user.id,data={}),Consent(user_id=user.id)])
        db.commit()
    print('Administrador criado.')
