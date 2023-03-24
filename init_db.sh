#!/bin/bash
rm -f mymdb.sqlite
touch mymdb.sqlite
echo "CREATE TABLE IF NOT EXISTS movies (
    rank INTEGER,
    title VARCHAR PRIMARY KEY,
    watched BOOLEAN,
    created_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
" | sqlite3 mymdb.sqlite
