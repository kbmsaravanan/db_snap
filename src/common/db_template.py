CREATE_TABLE = "create table {schema}.{table_name} ( \n{columns}\n\t{constraints}"
COLUMN = "\t{column_name} {type} {nullable} {default},\n"
ALTER_ADD_COLUMN = "alter table {table_name} add column {column_name} {data_type} {nullable} {default};\n"
ALTER_COLUMN_TYPE = (
    "alter table {table_name} alter column {column_name} TYPE {data_type};\n"
)
ALTER_COLUMN_NULL = (
    "alter table {table_name} alter column {column_name} {is_nullable};\n"
)
ALTER_COLUMN_DEFAULT = (
    "alter table {table_name} alter column {column_name} {default};\n"
)
DROP_COLUMN = "alter table {table_name} drop column {column_name};\n"
DROP_TABLE = "drop table {table_name}; \n"
DROP_FUNCTION = "drop function {function_name}; \n"
ADD_CONSTRAINT = (
    "alter table {table_name} add {constraint_def};\n"
)

TABLE_SCHEMA_QUERY = (
    "select table_schema, table_name, column_name, data_type, character_maximum_length, numeric_precision, "
    "numeric_scale, column_default, is_nullable, ordinal_position from INFORMATION_SCHEMA.columns "
    "where table_catalog = '{database}' and table_schema != 'pg_catalog' "
    "and table_schema != 'information_schema' "
    "order by table_name, ordinal_position;"
)

CONSTRAINT_SCHEMA_QUERY = (
    "select distinct c.table_schema, c.table_name, c.constraint_type, "
    "pg_catalog.pg_get_constraintdef(con.oid, true) constraint_def "
    "from pg_catalog.pg_constraint con "
    "join information_schema.table_constraints c on c.constraint_name = con.conname "
    "join information_schema.key_column_usage kcu on kcu.constraint_name = c.constraint_name "
    "where c.constraint_catalog = '{database}' and c.constraint_schema != 'pg_catalog' "
    "and c.constraint_schema != 'information_schema' and kcu.constraint_catalog = '{database}'; "
)

INDEX_SCHEMA_QUERY = (
    "select schemaname, tablename, indexname, indexdef from pg_catalog.pg_indexes i "
    "left join pg_catalog.pg_constraint c on i.indexname = c.conname "
    "where schemaname != 'pg_catalog' and schemaname != 'information_schema' and c.conname is null;"
)

FUNCTION_SCHEMA_QUERY = (
    "select n.nspname as schema_name, p.proname as function_name, l.lanname as function_language, "
    "case when l.lanname = 'internal' then p.prosrc else pg_get_functiondef(p.oid) end as function_def, "
    "pg_get_function_arguments(p.oid) as function_arguments, t.typname as return_type from pg_proc p "
    "left join pg_namespace n on p.pronamespace = n.oid left join pg_language l on p.prolang = l.oid "
    "left join pg_type t on t.oid = p.prorettype where n.nspname not in ('pg_catalog', 'information_schema') "
    "order by schema_name, function_name;"
)
