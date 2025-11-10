#!/usr/bin/env python

import argparse

from sqlalchemy import URL, Engine, create_engine, text
from sqlalchemy.dialects.postgresql import dialect as postgresql_dialect
from sqlalchemy.schema import CreateTable

from brain_region_extractor.database import Base
from brain_region_extractor.util import print_error_exit, read_environment_variable


def create_database(engine: Engine):
    try:
        with engine.connect() as connection:
            print("Enabling PostGIS extensions...")
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            connection.commit()
            print("PostGIS extensions enabled.")

        print("🗃️ Creating tables...")
        Base.metadata.create_all(engine)
        print("Tables created.")
    except Exception as error:
        print_error_exit(f"Error while creating the database:\n{error}")


def print_create_database() -> None:
    dialect = postgresql_dialect()
    for table in Base.metadata.sorted_tables:
        statement = CreateTable(table)
        print(statement.compile(dialect=dialect))


def get_engine() -> Engine:
    print("Connecting to the database...")

    url = URL.create(
        drivername = 'postgresql',
        host       = read_environment_variable("POSTGIS_HOST"),
        port       = int(read_environment_variable("POSTGIS_PORT")),
        username   = read_environment_variable("POSTGIS_USERNAME"),
        password   = read_environment_variable("POSTGIS_PASSWORD"),
        database   = read_environment_variable("POSTGIS_DATABASE"),
    )

    return create_engine(url)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or reset the PostGIS MRI scans database.")

    parser.add_argument(
        "--print-sql",
        action="store_true",
        help="Print the SQL statements instead of executing them."
    )

    args = parser.parse_args()

    if args.print_sql:
        print_create_database()
        return

    engine = get_engine()
    create_database(engine)
    print("Database setup completed!")


if __name__ == '__main__':
    main()
