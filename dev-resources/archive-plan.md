# Archive Plan

## Infrastructure
- AWS S3

## File organisation
- [sqlite-s3vfs](https://github.com/uktrade/sqlite-s3vfs)

## Description
In order to archive our old data, we will upload it to a SQLite archive in an S3 bucket. We will interface with it via sqlite-s3vfs to allow for more efficient transactions. This yields two main benefits:
- By hosting the data on S3, we enjoy lower costs than on the MS SQL Server
- By using the SQLite format, we save space and also minimise costs
- By using the SQLite format, we also provide an efficient, if relatively slow, mechanism for querying historical data

## Discussion
- This is preferable to a database or data warehouse for the lower cost of retrieval
- This is preferable to a compact file format, like parquet, for more efficient queries, not requiring all data to be read into memory for analysis.
