# complaint-search
Experimenting building python modules that query elasticsearch

This repository assumes that you have an instance of elasticsearch running with complaint data set up and running.

## Installation

This project uses environment variables and uses autoenv to automatically define environement variables and launch the virtualenv upon cding to the project folder.

You will need to install Autoenv if you haven't:
```
brew install autoenv
```

After installation, Homebrew will output instructions similar to:

To finish the installation, source activate.sh in your shell:
  source /Users/[YOUR USERNAME]/homebrew/opt/autoenv/activate.sh
Run that now for your initial setup. Any time you run the project you’ll need to run that last line, so if you’ll be working with the project consistently, we suggest adding it to your Bash profile by running:

echo 'source /Users/[YOUR USERNAME]/homebrew/opt/autoenv/activate.sh' >> ~/.bash_profile
If you need to find this info again later, you can run:

brew info autoenv

You can then copy the `.env_SAMPLE` file to `.env`, then update any environment variables accordingly.

Then you can install all dependencies in the `requirements.txt`
```
pip install -r requirements.txt
```

## Testing
Right now you can run `complaint_search.py` to make sure everything runs successfully
```
python complaint_search.py
```