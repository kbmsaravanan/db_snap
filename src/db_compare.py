from functools import reduce
import common.main as sh
import json
import shutil
import os
import common.db_template as template


def compare_src_to_dest():
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
        shutil.copytree(
            r"{schema}\\tables".format(schema=src_snapshot.schema),
            r"migrate_scripts\\tables",
        )
        shutil.copytree(
            r"{schema}\\constraints".format(schema=src_snapshot.schema),
            r"migrate_scripts\\constraints",
        )
        print("Create all tables")
        return

    if not os.path.isdir(r"migrate_scripts\tables"):
        os.makedirs(r"migrate_scripts\tables")
        os.makedirs(r"migrate_scripts\constraints")

    compare_tables(src_snapshot.schema, src_snapshot.tables, dest_snapshot.tables)
    compare_function(src_snapshot.functions, dest_snapshot.functions)


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


def compare_tables(schema, src_tables, dest_tables):
    constraint_str = ""
    for src_table in src_tables:
        table_str = ""
        alter_str = ""
        dest_table = list(
            filter(lambda x: x.table_name == src_table.table_name, dest_tables)
        )

        if not dest_table:
            shutil.copyfile(
                r"{0}\tables\{1}.sql".format(schema, src_table.table_name),
                r"migrate_scripts\tables\{1}.sql".format(schema, src_table.table_name),
            )
            constraint_str += generate_foreignkey_script(
                src_table.table_name, src_table.constraints, []
            )
            continue

        alter_str += compare_columns(
            src_table.table_name, src_table.columns, dest_table[0].columns
        )
        alter_str += compare_indexes(
            src_table.table_name, src_table.indexes, dest_table[0].indexes
        )
        constraint_str += generate_foreignkey_script(
            src_table.table_name, src_table.constraints, dest_table[0].constraints
        )
        src_constraints = list(
            filter(lambda x: x.constraint_type != "FOREIGN KEY", src_table.constraints)
        )
        des_constraints = list(
            filter(
                lambda x: x.constraint_type != "FOREIGN KEY", dest_table[0].constraints
            )
        )
        alter_str += compare_constraints(
            src_table.table_name, src_constraints, des_constraints
        )

        if alter_str:
            table_str += alter_str
            index = dest_tables.index(dest_table[0])
            dest_tables.pop(index)
        create_write_file(
            r"migrate_scripts\tables\{1}.sql".format(schema, src_table.table_name),
            table_str,
        )

    for dest_table in dest_tables:
        count = len(
            list(filter(lambda x: x.table_name == dest_table.table_name, src_tables))
        )
        if count == 0:
            drop_str = template.DROP_TABLE.format(table_name=dest_table.table_name)
            table_str += drop_str
        create_write_file(
            r"migrate_scripts\tables\{1}.sql".format(schema, src_table.table_name),
            table_str,
        )
    create_write_file(
        r"migrate_scripts\constraints\keys.sql",
        constraint_str,
    )


def create_write_file(filename_with_path, filedata):
    if filedata != "":
        table_file = open(filename_with_path, "w")
        table_file.write(filedata)


def generate_foreignkey_script(table_name, src_constraints, des_constraints):
    src_constraints_list = list(
        filter(lambda x: x.constraint_type == "FOREIGN KEY", src_constraints)
    )
    des_constraints_list = list(
        filter(lambda x: x.constraint_type == "FOREIGN KEY", des_constraints)
    )
    return compare_constraints(table_name, src_constraints_list, des_constraints_list)


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
        des_index = list(filter(lambda x: x.indexname == src.indexname, dest_indexes))
        if not des_index:
            alter_str += src.indexdef
    return alter_str


def compare_constraints(table_name, src_constraints, dest_constraints):
    alter_str = ""
    for src in src_constraints:
        dest_constraint = list(
            filter(lambda x: x.constraint_def == src.constraint_def, dest_constraints)
        )
        if not dest_constraint:
            alter_str += template.ADD_CONSTRAINT.format(
                table_name=table_name, constraint_def=src.constraint_def
            )
    return alter_str


if __name__ == "__main__":
    compare_src_to_dest()
