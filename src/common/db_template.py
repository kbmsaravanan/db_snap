CREATE_TABLE = "CREATE TABLE {schema}.{table_name} ( \n{columns}\n\t{constraints}"
COLUMN = "\t{column_name} {type} {nullable} {default},\n"
ALTER_ADD_COLUMN = "ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type} {nullable} {default};\n"
ALTER_COLUMN_TYPE = (
    "ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {data_type};\n"
)
ALTER_COLUMN_NULL = (
    "ALTER TABLE {table_name} ALTER COLUMN {column_name} {is_nullable};\n"
)
ALTER_COLUMN_DEFAULT = (
    "ALTER TABLE {table_name} ALTER COLUMN {column_name} {default};\n"
)
DROP_COLUMN = "ALTER TABLE {table_name} DROP COLUMN {column_name};\n"
DROP_TABLE = "DROP TABLE {table_name}; \n"
DROP_FUNCTION = "DROP function {function_name}; \n"

TABLE_SCHEMA_QUERY = (
    "select table_schema, table_name, column_name, data_type, character_maximum_length, numeric_precision, "
    "numeric_scale, column_default, is_nullable, ordinal_position from INFORMATION_SCHEMA.columns "
    "where table_catalog = '{database}' and table_schema != 'pg_catalog' "
    "and table_schema != 'information_schema' "
    "order by table_name, ordinal_position;"
)

CONSTRAINT_SCHEMA_QUERY = (
    "select c.table_schema, c.table_name, c.constraint_type, "
    "pg_catalog.pg_get_constraintdef(con.oid, true) constraint_def "
    "from pg_catalog.pg_constraint con "
    "join information_schema.table_constraints c on c.constraint_name = con.conname "
    "join information_schema.key_column_usage kcu on kcu.constraint_name = c.constraint_name "
    "where c.constraint_catalog = '{database}' and c.constraint_schema != 'pg_catalog' "
    "and c.constraint_schema != 'information_schema' and kcu.constraint_catalog = '{database}' "
    "order by kcu.table_schema, kcu.table_name, kcu.ordinal_position;"
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
