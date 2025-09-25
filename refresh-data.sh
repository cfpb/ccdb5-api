#!/bin/sh

# ==========================================================================
# Import data from a gzipped dump. Provide the filename as the first arg.
# NOTE: Run this script while in the project root directory.
#       It will not run correctly when run from another directory.
# ==========================================================================

set -e

usage() {
    cat << EOF
Please download a recent database dump before running this script:

  ./refresh-data.sh production_django.sql.gz

Or you can define the location of a dump and this script will
download it for you:

  export DB_DUMP_URL=https://example.com/production_django.sql.gz
  ./refresh-data.sh

EOF
    exit 1;
}

download_data() {
    echo 'Downloading database dump...'
    skip_download=0

    # If the file already exists, check its timestamp, and skip the download
    # if it matches the timestamp of the remote file.
    if [ -f "$refresh_dump_name" ]; then
        timestamp_check=$(curl -s -I -R -L -z "$refresh_dump_name" "${DB_DUMP_URL}")
        if [ -z "${$timestamp_check##*'304 Not Modified'*}" ]; then
            echo 'Skipping download as local timestamp matches remote timestamp'
            skip_download=1
        fi
    fi

    if [ "$skip_download" = "0" ]; then
        curl -RL -o "$refresh_dump_name" "${DB_DUMP_URL}"
    fi
}

check_data() {
    echo 'Validating local dump file'
    gunzip -t "$refresh_dump_name"
}

refresh_data() {
    echo 'Importing refresh db'
    gunzip < "$refresh_dump_name" | cfgov/manage.py dbshell > /dev/null
    SCHEMA="$(gunzip -c $refresh_dump_name | grep -m 1 'CREATE SCHEMA' | sed 's/CREATE SCHEMA \(.*\);$/\1/')"
    PGUSER="${PGUSER:-cfpb}"
    if [ "${PGUSER}" != "${SCHEMA}" ]; then
      echo "Adjusting schema name to match username..."
      echo "DROP SCHEMA IF EXISTS \"${PGUSER}\" CASCADE; \
        ALTER SCHEMA \"${SCHEMA}\" RENAME TO \"${PGUSER}\"" | psql > /dev/null 2>&1
    fi
    echo 'Running any necessary migrations'
    ./cfgov/manage.py migrate --noinput --fake-initial
    echo 'Setting up initial data'
    ./cfgov/manage.py runscript initial_data
}

get_data() {
    if [ -z "$refresh_dump_name" ]; then
        if [ -z "$DB_DUMP_URL" ]; then
            usage
        fi
        # Split URL, and get the file name.
        refresh_dump_name="$(echo $DB_DUMP_URL | tr '/' '\n' | tail -1)"
        download_data
    else
        if [ $refresh_dump_name != *.sql.gz ]; then
            echo "Input dump '$refresh_dump_name' expected to end with .sql.gz."
            exit 2
        fi
    fi
}

refresh_dump_name=$@

get_data
check_data
refresh_data
