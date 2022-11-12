import json
import common.main as sh
import common.db_template as template


def get_table_indexes(index_list):
    index_str = ""
    for index in index_list:
        index_str += index.indexdef + ";\n"
    return index_str


def get_table_key_constraints(key_list):
    key_str = ""
    for key in key_list:
        key_str += key.constraint_def + ",\n\t"
    return key_str


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
        if column.numeric_precision is None and column.numeric_scale is None:
            return "numeric"
        else:
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


def create_table_column(column, cname_padding, type_padding):
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

    return template.COLUMN.format(
        column_name=to_case_sensitive(column_name).ljust(cname_padding),
        type=data_type.ljust(type_padding),
        nullable=is_nullable,
        default=default,
    )


def create_table_schema(schema, table):
    column_script = ""
    column_list = table.columns
    max_col_length = len(max(list(map(lambda x: x.column_name, column_list)), key=len))
    max_type_length = len(max(list(map(lambda x: x.data_type, column_list)), key=len))
    for column in column_list:
        column_script += create_table_column(column, max_col_length, max_type_length)
    key_script = get_table_key_constraints(
        list(filter(lambda x: x.constraint_type != "FOREIGN KEY", table.constraints))
    )
    index_script = get_table_indexes(table.indexes)
    table_script = template.CREATE_TABLE.format(
        schema=schema,
        table_name=to_case_sensitive(table.table_name),
        columns=column_script[:-1],
        constraints=key_script[:-1],
    )
    return table_script[:-2] + "\n);\n" + index_script


def create_schema_script():
    sh.generate_snap()
    sh_file = open(r"snapshot\snap.json", "r")
    snapshot = sh.snapshot_from_dict(json.loads(sh_file.read()))
    constrains = ""
    for table in snapshot.tables:
        table_script = create_table_schema(snapshot.schema, table)
        table_file = open(
            r"{0}\tables\{1}.sql".format(snapshot.schema, table.table_name), "w"
        )
        table_file.write(table_script)
        for key in table.constraints:
            if key.constraint_type == "FOREIGN KEY":
                constrains += template.ADD_CONSTRAINT.format(
                    table_name=table.table_name, constraint_def=key.constraint_def
                )
    if constrains != "":
        constraint_file = open(r"{0}\constraints\keys.sql".format(snapshot.schema), "w")
        constraint_file.write(constrains)

    for function in snapshot.functions:
        function_file = open(
            r"{0}\functions\{1}.sql".format(snapshot.schema, function.function_name),
            "w",
        )
        function_file.write(function.function_def.replace("\r", ""))


def to_case_sensitive(str):
    if any(x.isupper() for x in str):
        return '"' + str + '"'
    else:
        return str


if __name__ == "__main__":
    create_schema_script()
