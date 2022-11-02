import psycopg2
import configparser as cp
import json
import snap as Snapshot


def snapshot_from_dict(s):
    return Snapshot.snap_from_dict(s)


def snapshot_to_dict(x):
    return Snapshot.snap_to_dict(Snapshot, x)


database = ''
connection = None


def __set_connection(config_section):
    global database, connection
    try:
        config = cp.ConfigParser()
        config.read('src\settings.ini')
        database = config[config_section]['database']
        connection = psycopg2.connect(user=config[config_section]['user'],
                                      password=config[config_section]['password'],
                                      host=config[config_section]['host'],
                                      port=config[config_section]['port'],
                                      database=config[config_section]['database'])
    except Exception as error:
        print("Connection failed", error)


def __get_all(query):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as error:
        print("An exception has occured:", error)
        print("Exception TYPE:", type(error))
        return []
    finally:
        if cursor is not None:
            cursor.close()


def __get_table_schema():
    query = "select table_schema, table_name, column_name, data_type, character_maximum_length, numeric_precision, " \
            "numeric_scale, column_default, is_nullable, ordinal_position from INFORMATION_SCHEMA.columns " \
            "where table_catalog = '{database}' and table_schema != 'pg_catalog' " \
            "and table_schema != 'information_schema' " \
            "order by table_name, ordinal_position;".format(database=database)
    return __get_all(query)


def __get_constraint_schema():
    query = "select c.table_schema, c.table_name, c.constraint_type, " \
            "pg_catalog.pg_get_constraintdef(con.oid, true) constraint_def " \
            "from pg_catalog.pg_constraint con " \
            "join information_schema.table_constraints c on c.constraint_name = con.conname " \
            "join information_schema.key_column_usage kcu on kcu.constraint_name = c.constraint_name " \
            "where c.constraint_catalog = '{database}' and c.constraint_schema != 'pg_catalog' " \
            "and c.constraint_schema != 'information_schema' and kcu.constraint_catalog = '{database}' " \
            "order by kcu.table_schema, kcu.table_name, kcu.ordinal_position;".format(
                database=database)
    return __get_all(query)


def __get_index_schema():
    query = "select schemaname, tablename, indexname, indexdef from pg_catalog.pg_indexes i " \
            "left join pg_catalog.pg_constraint c on i.indexname = c.conname " \
            "where schemaname != 'pg_catalog' and schemaname != 'information_schema' and c.conname is null;"
    return __get_all(query)


def __get_function_schema():
    query = "select n.nspname as schema_name, p.proname as function_name, l.lanname as function_language, "\
            "case when l.lanname = 'internal' then p.prosrc else pg_get_functiondef(p.oid) end as function_def, "\
            "pg_get_function_arguments(p.oid) as function_arguments, t.typname as return_type from pg_proc p "\
            "left join pg_namespace n on p.pronamespace = n.oid left join pg_language l on p.prolang = l.oid "\
            "left join pg_type t on t.oid = p.prorettype where n.nspname not in ('pg_catalog', 'information_schema') "\
            "order by schema_name, function_name;"
    return __get_all(query)


def __get_columns(column_list):
    columns = []
    for r in column_list:
        c = Snapshot.Column(r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9])
        columns.append(c)
    return columns


def __get_constraints(constraint_list):
    constraints = []
    for r in constraint_list:
        c = Snapshot.Constraint(r[2], r[3])
        constraints.append(c)
    return constraints


def __get_indexes(index_list):
    indexes = []
    for r in index_list:
        c = Snapshot.Index(r[2], r[3])
        indexes.append(c)
    return indexes


def __get_tables(table_list, constraints, indexes):
    tables = []
    table_names = set(map(lambda x: x[1], table_list))
    for t in table_names:
        ts = Snapshot.Table(t, __get_columns(list(filter(lambda x: x[1] == t, table_list))),
                            __get_constraints(
            list(filter(lambda x: x[1] == t, constraints))),
            __get_indexes(list(filter(lambda x: x[1] == t, indexes))))
        tables.append(ts)
    return tables


def __get_functions(function_list):
    functions = []
    for r in function_list:
        c = Snapshot.Function(r[1], r[2], r[3], r[4], r[5])
        functions.append(c)
    return functions


def get_snapshot(config_section):
    __set_connection(config_section)
    tbl_schema = __get_table_schema()
    constraint_schema = __get_constraint_schema()
    index_schema = __get_index_schema()
    function_schema = __get_function_schema()
    if tbl_schema.__len__() == 0:
        return Snapshot.Snap("public", [])
    schema_list = list(set(map(lambda x: x[0], tbl_schema)))
    snap_shot = Snapshot.Snap(schema_list[0],
                         __get_tables(list(filter(lambda x: x[0] == schema_list[0], tbl_schema)),
                                      list(
                                          filter(lambda x: x[0] == schema_list[0], constraint_schema)),
                                      list(
                                          filter(lambda x: x[0] == schema_list[0], index_schema))
                                      ),
                         __get_functions(list(filter(lambda x: x[0] == schema_list[0],function_schema)))
                         )
    connection.close()
    return snap_shot


def generate_snap(config_section):
    snap = get_snapshot(config_section)
    w_file = open(r'snapshot\snap.json', 'w')
    w_file.write(json.dumps(
        snap, default=lambda o: o.__dict__, sort_keys=False))


if __name__ == "__main__":
    w_file = open(r'snapshot\snap.json', 'w')
    w_file.write(json.dumps(get_snapshot(),
                            default=lambda o: o.__dict__, sort_keys=False))
