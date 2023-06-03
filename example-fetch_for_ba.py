import hourly_co2_intensity_usa

# example
excel_path = hourly_co2_intensity_usa.fetch_hourly_co2_spreadsheet("https://www.eia.gov/electricity/gridmonitor/knownissues/xls/WAUW.xlsx")
rows_with_data = hourly_co2_intensity_usa.rows_with_co2_data_from_excel(excel_path)
readings = hourly_co2_intensity_usa.create_readings_from_rows(rows_with_data)
hourly_co2_intensity_usa.add_readings_to_db("hourly-co2-usa.db", readings)

hourly_co2_intensity_usa.create_parquet_file_from_db("hourly-co2-usa.db", "hourly-co2-usa.ztd.parquet")

