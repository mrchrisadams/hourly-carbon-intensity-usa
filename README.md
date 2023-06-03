##  hourly carbon intensity figures for electricity in the USA

This repo is the result of a conversation at the LF Energy forum about how it would be _really_ nice to have easy access to data about the average carbon intensity of electricity consumption for a given country, at a fairly high temporal resolution (i.e. hourly), and at a fairly good geographic resolution (i.e. balancing authority).

We talk about electricity consumption because if you are consuming electricity from the grid, and you care about its carbon intensity, then looking at the generation figures by themselves can give misleading results. 

For temporal resolution, hourly resolution allows you to see the changes in carbon intensity over a given day. It's high enough resolution to reflect the sun coming up and setting for example.

For geographic resolution, having data at a balancing authority level lets you see the impact of decisions being made by one operator of that part of the grid in terms of ramping up fossil fuel powered generation, and so on.


## Why not just use the EIA API? It's free and well designed!

Currently this information is not available via the EIA API data portal, but it _is_ available if you know to:

1. download a series of 30mb+ excel files for each balancing authority every day
2. look for new values added to a specific column in each spreadsheet
3. pull the data out and load into your own ETL pipeline.

This project pretty much does these steps, and makes the data points available in a sqlite database that is easy to query, as well as creating parquet files that have the same data in very portable, easily queryable form.

## What is it in more detail

This repo contains a python script that will

1. fetch the latest hourly carbon intensity for a given balancing authority
2. pull out the rows representing hours of electricty generation that have values for the carbon intensity of consuming it
3. puts it into a sqlite database
4. creates a compressed parquet file from the sqlite database that is much much smaller

For convenience, it includes datasette, so you can make the SQlite database avialable for easy querying.



# TODO

- [x] Figure out the columns we need for understanding carbon intensity of electricity we consume
- [x] Figure out how pull data out of excel file in python
- [x] Figure out how to make small parquet file of the data for easy fast querying
- [ ] Confirm data licensing
- [ ] Write github action to fetch the hourly co2 figures for every balancing authority listed on a regular basis, and put the parquet file somewhere online

# Contributing

Pull requests are very gratefully accepted.