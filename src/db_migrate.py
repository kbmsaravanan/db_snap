import psycopg2
import os
import configparser as cp


def get_connection():
    try:
        config_section = "db_connection"
        config = cp.ConfigParser()
        config.read("src\settings.ini")
        return psycopg2.connect(
            user=config[config_section]["user"],
            password=config[config_section]["password"],
            host=config[config_section]["host"],
            port=config[config_section]["port"],
            database=config[config_section]["database"],
        )
    except Exception as error:
        print("Connection failed", error)


def execute_scripts():
    table_path = r"migrate_scripts\tables"
    table_list = os.listdir(table_path)
    # fkey_path = r'migrate_scripts\foreignkey'
    # if os.path.isdir(fkey_path):
    #     fkey_list = os.listdir(fkey_path)
    # else:
    #     fkey_list = []
    connection = get_connection()
    cursor = connection.cursor()

    for table in table_list:
        tbl_file = open(os.path.join(table_path, table), "r")
        tbl_script = tbl_file.read()
        cursor.execute(tbl_script)

    # for fkey in fkey_list:
    #     fkey_file = open(os.path.join(fkey_path, fkey), 'r')
    #     fkey_script = fkey_file.read()
    #     cursor.execute(fkey_script)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    execute_scripts()
