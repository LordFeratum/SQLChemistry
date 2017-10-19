import logging

from aiomysql import create_pool, connect, DictCursor

from sqlchemistry.engine.base import BaseEngine
from sqlchemistry.sql.base import ResultQuery
from sqlchemistry.sql.backends.mysql import MySQLQuery



class MySQLEngine(BaseEngine):
    EQUALS = '='
    AND = 'AND'
    OR = 'OR'

    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        super(MySQLEngine, self).__init__(*args, **kwargs)

    async def _connect(self):
        self._logger.debug('Connecting...')
        credentials = {
            'host': self._host,
            'port': int(self._port or '3306'),
            'user': self._user,
            'password': self._pwd,
            'db': self._db,
            'autocommit': self._autocommit,
            'loop': self._loop
        }

        if self._use_pool:
            self._pool = await create_pool(**credentials)

        else:
            self._connection = await connect(**credentials)

    def get_dbapi_identifier(self, identifier):
        return '%({})s'.format(identifier)

    def get_query(self, table, columns=None):
        return MySQLQuery(self, table, columns=columns or table.columns())

    async def commit(self):
        await self._connection.commit()

    async def execute(self, query, params, echo=False):
        async with self._connection.cursor() as cur:
            if echo:
                print(cur.mogrify(query, params))
            await cur.execute(query, params)
            return cur.lastrowid

    async def create_table(self, table, check_exists, echo):
        def _process_column(column):
            params = {
                'name': column.name,
                'type': column.sql_type,
                'nullable': ' NOT NULL' if column.is_nullable() else '',
                'pk': ' PRIMARY KEY' if column.is_primary_key() else '',
                'inc': ' AUTO_INCREMENT' if column.is_autoincrement() else ''
            }
            return '\t{name} {type}{nullable}{inc}{pk}'.format(**params)

        def _process_foreign_key(column):
            foreign = column.get_foreign_key()
            return (
                f"\tFOREIGN KEY ({column.name})\n"
                f"\tREFERENCES {foreign.tablename}({foreign.name})"
            )

        exists = '' if not check_exists else 'IF NOT EXISTS'
        table._init_columns({})
        columns = ',\n'.join(_process_column(c) for c in table.columns())
        foreign_keys = ',\n'.join(
            _process_foreign_key(c) for c in table.columns()
            if c.is_foreign_key()
        )

        if foreign_keys:
            columns += ',\n'

        corpus = (
            f"CREATE TABLE {exists} {table.tablename()} (\n"
            f"{columns} \n"
            f"{foreign_keys}\n"
             ");"
        )

        return await self.execute(corpus, None, echo=echo)

    async def insert(self, entity):
        keys, values = [], []
        params = {}
        for column in entity.columns():
            if column.get_value() is None:
                continue

            keys.append(column.name)
            values.append(f'%({column.name})s')
            params[column.name] = column.get_value()

        keys = '(' + ', '.join(keys) + ')'
        values = '(' + ', '.join(values) + ')'

        primary_key = entity.primary_keys()[0].name

        sql = (f'INSERT INTO {entity.tablename()} {keys} '
               f'VALUES {values} ')
        last_row_id = await self.execute(sql, params)
        setattr(entity, primary_key, last_row_id)

    async def fetchone(self, table, query, params):
        async with self._connection.cursor(DictCursor) as cur:
            await cur.execute(query, params)
            res = await cur.fetchone()
            return table(**res)


    async def fetchall(self, table, query, params):
        async with self._connection.cursor(DictCursor) as cur:
            await cur.execute(query, params)
            res = await cur.fetchall()
            return ResultQuery(table, res)
