# ccdb5-api
Experimenting building python modules that query elasticsearch

This repository assumes that you have an instance of elasticsearch running with complaint data set up and running.

## Installation

### As a Standalone

#### Environment Variables
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

#### Dependencies
Then you can install all dependencies in the `requirements.txt`
```shell
pip install -r requirements.txt
```

#### Testing
Right now you can run `complaint_search.py` to make sure everything runs successfully
```
python complaint_search.py
```

### As a Package
If you are installing this project as a package, you can pip install the following:
```shell
pip install -e git+https://github.com/cfpb/ccdb5-api.git@master#egg=ccdb5-api
```

This also assume that you have all the environment variables in your system, if not, please incorporate the environement variables in `.env` in your own project to make `complaint_search` works for you.

Once you pip installed this as a package you can use functions like so in your project:
```python
import complaint_search

complaint_search.search()
```
