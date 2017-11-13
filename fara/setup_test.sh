#!/bin/bash

# Install Selenium
pip install selenium

# Get the Gecko Driver for Firefox
wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz

# Extract folder and files
tar -xvzf geckodriver-*

# Make Executable
chmod +x geckodriver

# Make available in path
sudo mv geckodriver /usr/local/bin/

# Remove geckodriver tar ball file
sudo rm geckodriver-*

# Install pyvirtualdisplay to allow headless testing (Doesnt show up browser)
pip install pyvirtualdisplay

# Install xvfb library for Ubuntu (Required By pyvirtualdisplay)
sudo apt-get install xvfb

# Run test Command
python faraTestCase.py