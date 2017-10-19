from asyncio import get_event_loop

from sys import path
from os.path import join, dirname, abspath
from operator import and_, or_

path.insert(0, join(dirname(abspath(__file__)), '..'))

from sqlchemistry.session import Session
from sqlchemistry.types import Int, Boolean, Float, String
from sqlchemistry.sql.schema import Table, Column
from sqlchemistry.engine.backends.mysql import MySQLEngine


loop = get_event_loop()


class User(Table):
    __tablename__ = 'users'

    id = Column(Int, primary_key=True, autoincrement=True)
    paco = Column(Float)
    jamones = Column(Float(5))
    salsicha = Column(Boolean)
    string = Column(String)


async def main():
    dsn = "mysql+pymysql://user:user@localhost/sqlchemistry"
    ss = Session(MySQLEngine(dsn=dsn, loop=loop, use_pool=False))
    await ss.connect()
    await ss.create_table_if_not_exists(User, echo=True)

    query = ss.query(User)
    print(query)

    users = await query.all()
    print(users)

    for user in users:
        print(user)

    print("**********************************")

    for user in users:
        print(user)

    print("**********************************")

    print(users[2])


if __name__ == '__main__':
    loop.run_until_complete(main())