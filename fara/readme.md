## A Spider / Web Crawerl for FARA.GOV Active Principals

Author : Williams Isaac

** Description

This code contains a crawler to scrape active principals data from fara.gov website.

Extracted Data is in this format:
    {
        "url": "https://efile.fara.gov/pls/apex/f?p=171:200:0::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:6399,Exhibit%20AB,AFGHANISTAN", "country": "AFGHANISTAN", "foreign_principal": "Embassy of the Islamic Republic of Afghanistan", "reg_num": "6399", "state": "DC", "address": "2341 Wyoming Avenue, NWWashington  20008", "date": "2017-08-02T00:00:00", "registrant": "Sonoran Policy Group, LLC", "exhibit_url": ["http://www.fara.gov/docs/6399-Exhibit-AB-20170802-11.pdf"]
    },

## Usage

Install Python
    (This Code uses python 2.7 for development)
    https://www.python.org/downloads/

Install Scrapy
    pip install Scrapy

After Installation is done run this commant

    $ cd path/to/script
    $ scrapy crawl fara

Then you should see result in 
    fara_active_principals.json file


## Unit Testing

It isn't very easy testing spiders, so I wrote a simple test to simulate what the spider is supposed to look for. Like Tags, Classes, IDs, using XPath and CSS Selectiors

The Following Packages are used for Testing

    - Selenium (http://selenium-python.readthedocs.io)
    - geckodriver (https://github.com/mozilla/geckodriver/releases)
    - pyvirtualdisplay 
    - xvfb

This Package includes a setup_test.sh file which contains commands to install the packages and run the test script

Run this command on Ubuntu

    $ cd /path/to/farascrapper
    $ chmod 755 setup_test.sh
    $ ./setup_test.sh

If you have already run the first command and want to test again, run:

    $ python faraTestCase.py

The test works successfully on Linux - Ubuntu 16.04 LTS
And should work for MacOS too I suppose

## Thank You !