from sys import path
from os.path import join, dirname, abspath

path.insert(0, join(dirname(abspath(__file__)), '..'))


from sqlchemistry.session import Session
from sqlchemistry.types import Int, Boolean, Float, String
from sqlchemistry.sql.schema import Table, Column
from sqlchemistry.engine.backends.mysql import MySQLEngine


class User(Table):
    __tablename__ = 'users'

    id = Column(Int, primary_key=True, autoincrement=True)
    paco = Column(Float)
    jamones = Column(Float(5))
    salsicha = Column(Boolean)
    string = Column(String)


u = User()
u.paco = 12.0

a = u.paco
print(a)

print('Type: {} -- Value: {}'.format(type(u.paco), u.paco))
