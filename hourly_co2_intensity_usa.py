import typing
from sxl import Workbook
from sqlite_utils import Database
import sqlite3
import duckdb
from datetime import datetime

import httpx

from dataclasses import dataclass


@dataclass
class CO2IntensityReading:
    """
    A class to represent an hourly CO2 intensity reading
    from a balancing authority.
    """
    row_key:  str # for easy lookup and upserting
    ba: str # balancing authority code
    utc_recorded_at: datetime
    localtime_recorded_at: datetime
    co2_intensity: int


# example url
# https://www.eia.gov/electricity/gridmonitor/knownissues/xls/JEA.xlsx


def fetch_hourly_co2_spreadsheet(url: str) -> str:
    """
    Fetch the xlsx file containing the hourly carbon intensity figures
    for the balancing authority 
    """
    res = httpx.get(url)
    file_name = res.url.path.split('/')[-1]
    local_write_path = f"data/{file_name}"

    with open(f"data/{file_name}", "wb") as outfile:
        outfile.write(res.content)

    return local_write_path

def rows_with_co2_data_from_excel(workbook_path) -> typing.List[typing.List]:
    """
    Fetch the rows from the spreadsheet that have filled in 
    CO2 intensity consumption figures. These are usually added a 
    few days after the energy is generated in a given area.
    """
    wb = Workbook(workbook_path)
    hourly = wb.sheets['Published Hourly Data']
    # row[-1] is "CO2 Emissions Intensity for Consumed Electricity"
    rows_with_co2_data = [row for row in hourly.rows if row[-1] is not None]
    return rows_with_co2_data


def create_readings_from_rows(full_rows: typing.List[typing.List]):
    """
    Return just the balancing authority, the times and the energy consumption intensity, converted to grams"
    """
    
    LBS_TO_KILOS = 0.45359237
    simplified_rows = []
    for row in full_rows:
        reading = CO2IntensityReading(
            row_key = f"{row[0]}--{row[1]}",
            ba = row[0],
            utc_recorded_at = row[1],
            localtime_recorded_at = row[4],
            co2_intensity = row[-1]
        )
        simplified_rows.append(reading)

    return simplified_rows


def add_readings_to_db(sqlite_db_path: str, readings: typing.List[CO2IntensityReading]):
    """
    Add the readings to the sqlite database, using sqlite_utils. Rows that are
    """

    db = Database(sqlite_db_path)
    readings_table = db['readings']
    
    reading_dicts = [reading.__dict__ for reading in readings[1:]]

    readings_table.insert_all(reading_dicts, ignore=True, pk="row_key")


def create_parquet_file_from_db(sqlite_db_path: str, parquet_filepath: str):
    """
    Create a compressed parquet file of the readings
    """

    duck = duckdb.connect()
    # allow us to read the sqlite file
    duck.execute("INSTALL sqlite_scanner;")
    duck.execute("LOAD sqlite_scanner;")
    # create our table with typing that SQLite does not support, like TIMESTAMPS
    duck.execute("""
        CREATE TEMP TABLE reading_pqt(
            row_key VARCHAR, 
            ba VARCHAR, 
            utc_recorded_at TIMESTAMP , 
            localtime_recorded_at TIMESTAMP, 
            co2_intensity FLOAT
        );
        """
    )
    # load the contents duckdb from sqlite, to make a nice small parquet file
    duck.execute(f"INSERT INTO reading_pqt SELECT * FROM sqlite_scan('{sqlite_db_path}', 'readings');")
    duck.execute(f"COPY (SELECT * FROM reading_pqt) TO '{parquet_filepath}' (FORMAT 'parquet', COMPRESSION 'ZSTD');")
                 
