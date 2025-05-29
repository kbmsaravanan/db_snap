# db_snap

**db_snap** is a PostgreSQL database versioning and migration tool. It allows you to snapshot your database schema, compare it with previous versions, and generate migration scripts to keep your database schema in sync across environments.

## Features

- **Schema Snapshotting:** Capture the current state of your PostgreSQL schema as a JSON file.
- **Schema Comparison:** Compare the current database schema with a previous snapshot.
- **Migration Script Generation:** Automatically generate SQL scripts to migrate your database schema.
- **Migration Execution:** Apply generated migration scripts to your database.
- **Function Support:** Includes PostgreSQL functions in snapshot and migration.

## Directory Structure

```
.
├── migrate_scripts/         # Generated migration scripts (tables, constraints)
├── public/                  # Generated schema scripts (tables, constraints, functions)
├── scripts/                 # (Reserved for custom scripts)
├── snapshot/
│   └── snap.json            # Latest schema snapshot
├── src/
│   ├── db_compare.py        # Compare schemas and generate migration scripts
│   ├── db_migrate.py        # Execute migration scripts
│   ├── db_snapshot.py       # Generate schema snapshot and scripts
│   ├── settings.ini         # Database connection settings
│   └── common/
│       ├── main.py          # Core snapshot logic
│       ├── snap.py          # Schema data structures
│       └── db_template.py   # SQL templates and queries
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
└── .vscode/                 # VSCode settings
```

## Getting Started

### Prerequisites

- Python 3.7+
- PostgreSQL database
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```

### Configuration

Edit [`src/settings.ini`](src/settings.ini) to match your PostgreSQL connection:

```ini
[db_connection]
host = <your_host>
port = 5432
user = <your_user>
password = <your_password>
database = <your_database>
```

### Usage

#### 1. Generate a Schema Snapshot

Creates a snapshot of your current database schema in [`snapshot/snap.json`](snapshot/snap.json):

```sh
python src/db_snapshot.py
```

#### 2. Generate Schema Scripts

Creates SQL scripts for tables, constraints, and functions in the `public/` directory:

```sh
python src/db_snapshot.py
```

#### 3. Compare and Generate Migration Scripts

Compares the current database schema with the snapshot and generates migration scripts in [`migrate_scripts/`](migrate_scripts/):

```sh
python src/db_compare.py
```

#### 4. Apply Migration Scripts

Executes the generated migration scripts against your database:

```sh
python src/db_migrate.py
```

## How It Works

- **Snapshot:** [`generate_snap`](src/common/main.py) extracts schema info and saves it as JSON.
- **Schema Scripts:** [`create_schema_script`](src/db_snapshot.py) generates SQL scripts for schema objects.
- **Compare:** [`compare_src_to_dest`](src/db_compare.py) compares the snapshot with the current DB and generates migration scripts.
- **Migrate:** [`execute_scripts`](src/db_migrate.py) runs the migration scripts.

## License

This project is licensed under the GNU GPL v3.0 - see the [LICENSE](LICENSE) file for details.

---

*Author: Balamuthu Saravanan*
