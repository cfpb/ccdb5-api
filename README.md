[![Build Status](https://travis-ci.org/cfpb/ccdb5-api.svg?branch=master)](https://travis-ci.org/cfpb/ccdb5-api)[![Coverage Status](https://coveralls.io/repos/github/cfpb/ccdb5-api/badge.svg?branch=master)](https://coveralls.io/github/cfpb/ccdb5-api?branch=master)

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

## API Docs

Documentation for this repository is rendered via GitHub pages and [Swagger](https://swagger.io/docs/). They can be edited in the `docs/` directory, but to view or deploy them, you'll need to install the dependencies listed in the `requirements_docs.txt` file:

```
pip install -r requirements_docs.txt
```

You can then preview your changes locally by running `mkdocs serve` and then reviewing <http://127.0.0.1:8000/>

When your changes are ready, you can submit them as a normal pull request. After that, you can use this command to publish them:

```
mkdocs gh-deploy --clean
```

That pushes the necessary files to the `gh-pages` branch.

### Notes

- The `mkdocs gh-deploy` command will push any edits you've made locally to the `gh-pages` branch of the repository, whether you've committed them or not.
- Mkdocs will create a "site" directory locally when you use either `build`, `serve` or `gh-deploy`. This is used to assemble assets to be pushed to the gh-pages branch, but the `site/` directory itself doesn't need to be under version control. It can be deleted after a deploy.


##  Running Tests

```shell
$ python manage.py test
```
