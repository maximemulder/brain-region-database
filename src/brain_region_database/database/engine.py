import os

from sqlalchemy import URL, Engine, create_engine

from brain_region_database.util import read_environment_variable


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

    debug_variable = os.environ.get('POSTGIS_DEBUG')
    echo = debug_variable == 'true' or debug_variable == '1'
    return create_engine(url, echo=echo)
