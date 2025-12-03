#!/usr/bin/env python

import argparse

from sqlalchemy import Engine, inspect, text
from sqlalchemy.dialects.postgresql import dialect as postgresql_dialect
from sqlalchemy.schema import CreateTable

from brain_region_database.database.engine import get_engine
from brain_region_database.database.models import Base
from brain_region_database.util import print_error_exit


def create_database(engine: Engine):
    try:
        with engine.connect() as connection:
            print("Enabling PostGIS extension...")
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            connection.commit()

        if len(inspect(engine).get_table_names()) > 0:
            print("Dropping existing tables...")
            Base.metadata.drop_all(engine)

        print("Creating tables...")
        Base.metadata.create_all(engine)
    except Exception as error:
        print_error_exit(f"Error while creating the database:\n{error}")


def print_create_database() -> None:
    dialect = postgresql_dialect()
    for table in Base.metadata.sorted_tables:
        statement = CreateTable(table)
        print(statement.compile(dialect=dialect))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or reset the PostGIS MRI scans database.")

    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print the SQL statements instead of executing them."
    )

    args = parser.parse_args()

    if args.print_only:
        print_create_database()
        return

    engine = get_engine()
    create_database(engine)
    print("Success!")


if __name__ == '__main__':
    main()
