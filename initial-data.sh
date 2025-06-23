#!/bin/sh

# ==========================================================================
# Initialization script for a wagtail user and imported data.
# NOTE: Run this script while in the project root directory.
#       It will not run correctly when run from another directory.
# ==========================================================================

# Set script to exit on any errors.
set -e

# Import Data
import_data(){
    echo 'Running Django migrations...'
    ./manage.py migrate
    echo 'Creating any necessary Django database cache tables...'
    ./manage.py createcachetable
}

import_data
