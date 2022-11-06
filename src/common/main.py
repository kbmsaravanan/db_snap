import psycopg2
import configparser as cp
import json
import common.snap as Snapshot
import common.db_template as template


def snapshot_from_dict(s):
    return Snapshot.snap_from_dict(s)


def snapshot_to_dict(x):
    return Snapshot.snap_to_dict(Snapshot, x)


database = ""
connection = None


def __set_connection():
    global database, connection
    try:
        config_section = "db_connection"
        config = cp.ConfigParser()
        config.read("src\settings.ini")
        database = config[config_section]["database"]
        connection = psycopg2.connect(
            user=config[config_section]["user"],
            password=config[config_section]["password"],
            host=config[config_section]["host"],
            port=config[config_section]["port"],
            database=config[config_section]["database"],
        )
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
    query = template.TABLE_SCHEMA_QUERY.format(database=database)
    return __get_all(query)


def __get_constraint_schema():
    query = template.CONSTRAINT_SCHEMA_QUERY.format(database=database)
    return __get_all(query)


def __get_index_schema():
    query = template.INDEX_SCHEMA_QUERY
    return __get_all(query)


def __get_function_schema():
    query = template.FUNCTION_SCHEMA_QUERY
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
        ts = Snapshot.Table(
            t,
            __get_columns(list(filter(lambda x: x[1] == t, table_list))),
            __get_constraints(list(filter(lambda x: x[1] == t, constraints))),
            __get_indexes(list(filter(lambda x: x[1] == t, indexes))),
        )
        tables.append(ts)
    return tables


def __get_functions(function_list):
    functions = []
    for r in function_list:
        c = Snapshot.Function(r[1], r[2], r[3], r[4], r[5])
        functions.append(c)
    return functions


def get_snapshot():
    __set_connection()
    tbl_schema = __get_table_schema()
    constraint_schema = __get_constraint_schema()
    index_schema = __get_index_schema()
    function_schema = __get_function_schema()
    if tbl_schema.__len__() == 0:
        return Snapshot.Snap("public", [])
    schema_list = list(set(map(lambda x: x[0], tbl_schema)))
    snap_shot = Snapshot.Snap(
        schema_list[0],
        __get_tables(
            list(filter(lambda x: x[0] == schema_list[0], tbl_schema)),
            list(filter(lambda x: x[0] == schema_list[0], constraint_schema)),
            list(filter(lambda x: x[0] == schema_list[0], index_schema)),
        ),
        __get_functions(
            list(filter(lambda x: x[0] == schema_list[0], function_schema))
        ),
    )
    connection.close()
    return snap_shot


def generate_snap():
    snap = get_snapshot()
    w_file = open(r"snapshot\snap.json", "w")
    w_file.write(json.dumps(snap, default=lambda o: o.__dict__, sort_keys=False))


if __name__ == "__main__":
    generate_snap()
    # w_file = open(r'snapshot\snap.json', 'w')
    # w_file.write(json.dumps(get_snapshot(),
    #                         default=lambda o: o.__dict__, sort_keys=False))
