import flask
from flask import Flask, request
from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
Base = declarative_base()
engine = create_engine('postgresql://app:1234@127.0.0.1:5431/mytology')
Session = sessionmaker(bind=engine)


class HttpError(Exception):

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def http_error_handler(er: HttpError):
    response = flask.jsonify({'status': 'error', 'message': er.message})
    response.status_code = er.status_code
    return response


class Advert(Base, UserMixin):
    __tablename__ = 'advert'

    id = Column(Integer, primary_key=True)
    topic = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    user = Column(String, nullable=True, unique=True)
    create_date = Column(DateTime, server_default=func.now())


class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True, unique=True)
    psw = Column(String(100), nullable=True)


Base.metadata.create_all(engine)


def get_adv(session, advert_id):
    adv = session.query(Advert).get(advert_id)
    if adv is None:
        raise HttpError(404, 'advertisement does not exist')
    return adv


@app.route('/adv/<int:advert_id>', methods=['GET'])
def get(advert_id):
    with Session() as session:
        user = get_adv(session, advert_id)
        return {
            'topic': user.topic,
            'description': user.description,
            'create_date': user.create_date.isoformat()
        }


@app.route('/adv', methods=['POST'])
def post():
    user_data = request.json
    with Session() as session:
        new_adv = Advert(topic=user_data['topic'],
                         description=user_data['description'],
                         user=user_data['user'])
        session.add(new_adv)
        session.commit()
        return flask.jsonify({'status': 'ok', 'id': new_adv.id})


@app.route('/adv/<int:advert_id>', methods=['PATCH'])
def patch(advert_id):
    user_data = request.json
    with Session() as session:
        user = get_adv(session, advert_id)
        for key, value in user_data.items():
            setattr(user, key, value)
        session.commit()
    return flask.jsonify({'status': 'ok', 'advert changed': advert_id})


@app.route('/adv/<int:advert_id>', methods=['DELETE'])
def delete(advert_id):
    with Session() as session:
        user = get_adv(session, advert_id)
        session.delete(user)
        session.commit()
    return flask.jsonify({'status': 'ok', 'advert deleted': advert_id})


if __name__ == '__main__':
    app.run()
