import common.main as sh
import json
import shutil
import os
import common.db_template as template


def compare_src_to_dest():
    migrate_str = ""
    if os.path.isdir(r"migrate_scripts"):
        shutil.rmtree("migrate_scripts")
    sh_file = open(r"snapshot\snap.json", "r")
    src_snapshot = sh.snapshot_from_dict(json.loads(sh_file.read()))
    dest_snapshot = sh.get_snapshot()

    if src_snapshot is None:
        print("Error : source empty")
        return None

    if dest_snapshot is None or dest_snapshot.schema == "":
        print("Create schema")

    if dest_snapshot.tables.__len__() == 0:
        shutil.copytree(r"schema\\tables", r"migrate_scripts\\tables")
        print("Create all tables")
        return

    if not os.path.isdir(r"migrate_scripts\tables"):
        os.makedirs(r"migrate_scripts\tables")

    migrate_str += compare_tables(src_snapshot.tables, dest_snapshot.tables)
    migrate_str += compare_function(src_snapshot.functions, dest_snapshot.functions)


def compare_function(src_functions, dest_functions):
    function_str = ""
    for src_function in src_functions:
        dest_function = list(
            filter(
                lambda x: x.function_name == src_function.function_name, dest_functions
            )
        )
        if dest_function.__len__() == 0:
            function_str += src_function.function_def
        elif src_function.function_def != dest_function[0].function_def:
            function_str += src_function.function_def
        if function_str:
            index = dest_functions.index(dest_function[0])
            dest_functions.pop(index)

    for dest_function in dest_functions:
        function_str += template.DROP_FUNCTION.format(
            function_name=dest_function.function_name
        )
    return function_str


def compare_tables(src_tables, dest_tables):
    table_str = ""
    alter_str = ""
    for src_table in src_tables:
        dest_table = list(
            filter(lambda x: x.table_name == src_table.table_name, dest_tables)
        )
        if not dest_table:
            table_str += open(r"public\tables", src_table.table_name + ".sql")
        else:
            alter_str += compare_columns(
                src_table.table_name, src_table.columns, dest_table[0].columns
            )
            alter_str += compare_indexes(
                src_table.table_name, src_table.indexes, dest_table[0].indexes
            )
            if alter_str:
                table_str += alter_str
                index = dest_tables.index(dest_table[0])
                dest_tables.pop(index)

    for dest_table in dest_tables:
        drop_str = template.DROP_TABLE.format(table_name=dest_table.table_name)
        table_str += drop_str
    return table_str


def compare_columns(table_name, src_columns, dest_columns):
    src_columns = sorted(src_columns, key=lambda x: x.ordinal_position)
    dest_columns = sorted(dest_columns, key=lambda x: x.ordinal_position)
    alter_str = ""
    for src_col in src_columns:
        dest_col = list(
            filter(lambda x: x.column_name == src_col.column_name, dest_columns)
        )
        if not dest_col:
            alter_str += alter_add_column(table_name, src_col)
            continue
        elif src_col.data_type != dest_col[0].data_type:
            alter_str += alter_column_type(table_name, src_col)
        elif src_col.character_maximum_length != dest_col[0].character_maximum_length:
            alter_str += alter_column_length(table_name, src_col)
        elif (
            src_col.numeric_precision != dest_col[0].numeric_precision
            or src_col.numeric_scale != dest_col[0].numeric_scale
        ):
            alter_str += alter_column_length(table_name, src_col)
        elif src_col.is_nullable != dest_col[0].is_nullable:
            alter_str += alter_column_null(table_name, src_col)
        elif src_col.column_default != dest_col[0].column_default:
            alter_str += alter_column_default(table_name, src_col)
        index = dest_columns.index(dest_col[0])
        dest_columns.pop(index)
    for des_col in dest_columns:
        alter_str += drop_column(table_name, des_col)
    return alter_str


def get_column_type(column):
    if (
        column.data_type == "character varying"
        and column.character_maximum_length is None
    ):
        return "character varying"
    if column.data_type == "character varying":
        return "character varying({0})".format(int(column.character_maximum_length))
    elif column.data_type == "character":
        return "character({0})".format(int(column.character_maximum_length))
    elif column.data_type == "numeric":
        return "numeric({0},{1})".format(
            int(column.numeric_precision), int(column.numeric_scale)
        )
    else:
        return column.data_type


def get_serial_name(data_type):
    if data_type == "integer":
        return "serial"
    elif data_type == "bigint":
        return "bigserial"
    elif data_type == "smallint":
        return "smallserial"
    else:
        return ""


def alter_add_column(table_name, column):
    column_name = column.column_name
    data_type = get_column_type(column)
    is_nullable = "NULL" if (column.is_nullable == "YES") else "NOT NULL"
    default = column.column_default or ""
    if column.column_default is not None and column.column_default.startswith(
        "nextval("
    ):
        data_type = get_serial_name(column.data_type)
        default = ""
    elif column.column_default is not None:
        default = "DEFAULT " + default
    return template.ALTER_ADD_COLUMN.format(
        table_name=table_name,
        column_name=column_name,
        data_type=data_type,
        nullable=is_nullable,
        default=default,
    )


def alter_column_type(table_name, column):
    column_name = column.column_name
    data_type = get_column_type(column)
    return template.ALTER_COLUMN_TYPE.format(
        table_name=table_name, column_name=column_name, data_type=data_type
    )


def alter_column_length(table_name, column):
    column_name = column.column_name
    data_type = get_column_type(column)
    return template.ALTER_COLUMN_TYPE.format(
        table_name=table_name, column_name=column_name, data_type=data_type
    )


def alter_column_null(table_name, column):
    column_name = column.column_name
    is_nullable = "DROP NOT NULL" if (column.is_nullable == "YES") else "SET NOT NULL"
    return template.ALTER_COLUMN_NULL.format(
        table_name=table_name, column_name=column_name, is_nullable=is_nullable
    )


def alter_column_default(table_name, column):
    column_name = column.column_name
    default = (
        "DROP DEFAULT"
        if (column.column_default is None)
        else "SET DEFAULT " + column.column_default
    )
    return template.ALTER_COLUMN_DEFAULT.format(
        table_name=table_name, column_name=column_name, default=default
    )


def drop_column(table_name, column):
    column_name = column.column_name
    return template.DROP_COLUMN.format(table_name=table_name, column_name=column_name)


def compare_indexes(table_name, src_indexes, dest_indexes):
    alter_str = ""
    for src in src_indexes:
        des_index = list(filter(lambda x: x.indexname == src.indexname))
        if not des_index:
            alter_str += src.indexdef


if __name__ == "__main__":
    compare_src_to_dest()
