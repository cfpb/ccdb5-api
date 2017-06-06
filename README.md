ccdb5-api
================

An API that provides an interface to search complaint data.

## Features

* Search complaint data
* Suggest complaint data based on input
* Get complaint based on ID

## Requirements

Requirements are retrieved and/or build automatically via pip (see below).

* django - Web framework
* djangorestframework - Rest API framework
* elasticsearch - low level client for Elasticsearch
* requests - http requests to get different data format
* urllib3 - http client library to help format http URL

## API Docs

TBD

## Setup & Running
This repository assumes that you have an instance of elasticsearch running with complaint data set up and running.

### Environment Variables
This project uses environment variables and uses autoenv to automatically define environment variables and launch the virtualenv upon cding to the project folder.

You will need to install Autoenv if you haven't:
```shell
brew install autoenv
```

After installation, Homebrew will output instructions similar to:

```shell
To finish the installation, source activate.sh in your shell:
  source /Users/[YOUR USERNAME]/homebrew/opt/autoenv/activate.sh
```

Run that now for your initial setup. Any time you run the project you’ll need to run that last line, so if you’ll be working with the project consistently, we suggest adding it to your Bash profile by running:
```
echo 'source /Users/[YOUR USERNAME]/homebrew/opt/autoenv/activate.sh' >> ~/.bash_profile
```

If you need to find this info again later, you can run:
```shell
brew info autoenv
```

You can then copy the `.env_SAMPLE` file to `.env`, then update any environment variables accordingly.

### Dependencies
This project uses `requirements.txt` files for defining dependencies, so you
can get up and running with `pip`:

```shell
$ pip install -r requirements.txt       # modules required for execution
```

With that, you just need a few additional commands to get up and running:
```shell
$ python manage.py runserver
```

##  Running Tests

```shell
$ python manage.py test
```