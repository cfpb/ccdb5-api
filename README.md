![ci](https://github.com/cfpb/ccdb5-api/workflows/ci/badge.svg)[![Coverage Status](https://coveralls.io/repos/github/cfpb/ccdb5-api/badge.svg?branch=main)](https://coveralls.io/github/cfpb/ccdb5-api?branch=main)

ccdb5-api
================

An API that provides an interface to search complaint data.

## Features

* Search complaint data
* Suggest complaint data based on input
* Get complaint based on ID

## Requirements

Requirements are batch-installed via pip (see below).

* django - Web framework
* django-localflavor - Country-specific Django helpers
* djangorestframework - Rest API framework
* elasticsearch - low level client for Elasticsearch
* requests - http requests to get different data format


## Setup & Running
This repository assumes that you have an instance of elasticsearch running with complaint data set up and running.

If not, please refer to the [CCDB Data Pipeline](https://github.com/cfpb/ccdb-data-pipeline/blob/main/INSTALL.md) to
load data into Elasticsearch.

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
First, create a virtual environment for Python dependencies:
```
mkvirtualenv ccdb5-api
```

Next, use `pip` to install dependencies, which are defined in `setup.py`:
```
pip install -e '.[testing]'
```

With that, you just need a few additional commands to get up and running:
```
python manage.py runserver
```

## API Docs

[Documentation](https://cfpb.github.io/ccdb5-api/) for this repository is rendered via GitHub pages and [Swagger](https://swagger.io/docs/). They can be edited in the `docs/` directory, but to build or deploy them, you'll need to install docs requirements:

```
pip install -r docs_requirements.txt
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

If you have [Tox](https://tox.readthedocs.io/en/latest/) installed (recommended),
you can run the specs for this project with the `tox` command.

If not, this command will run the specs on the python version your local
environment has installed: `./manage.py test`.

If you run the tests via Tox, it will automatically display spec coverage information.
To get test coverage information outside of Tox, install [Coverage.py](https://coverage.readthedocs.io/en/coverage-4.5.1a/)
and run these commands:

```
coverage erase
coverage run manage.py test
coverage report
```
