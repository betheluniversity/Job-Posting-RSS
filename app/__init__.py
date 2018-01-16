from flask import Flask, render_template, make_response
import config
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
import requests
import datetime
from app import banner
import cx_Oracle

app = Flask(__name__)

# Banner Connection
banner_server = banner.Banner()


@app.route("/")
def index():
    return "Hello World"


@app.route("/scrape")
def scrape():
    # Uses Requests to grab the xml
    xml = requests.get(config.sitmap_xml, params=None)
    # Creates soup from bs4
    # TODO think about changing to a faster parser
    soup = BeautifulSoup(xml.text, "html.parser")
    # Loops through all links in XML, notated by the <loc> tag
    number = 0
    jobs = []
    # TODO Maybe force all commits to happen at once. (versus each loop)
    # For above change to be made, you will need to introduce the banner_server commit, etc., into __init__.py class
    for link in soup.find_all('loc'):
        jobs.append(page_scrape(link.get_text()))
        number = number + 1

    # return "Scraped from %s Job Listings." % number
    sitemap_xml = render_template('output.xml', **locals())
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


def get_iframe_link(link):
    webpage = requests.get(link, params=None)
    soup = BeautifulSoup(webpage.text, 'html.parser')
    element = soup.find("iframe")
    link = element["src"]
    return link


def page_scrape(link):
    # Variables needed to Scrape
    iframe_link = get_iframe_link(link)
    webpage = requests.get(iframe_link, params=None)
    soup = BeautifulSoup(webpage.text, 'html.parser')

    # Data the program is finding
    id_ = ""
    descrip = ""
    title = soup.find("h1")


    # TODO if there is an error, maybe save it
    # Prints the title
    print title.string

    unscraped_id = soup.find_all("div", "iCIMS_JobHeaderGroup")

    for group_with_id in unscraped_id:
        # Should only have to loop once
        id_group = group_with_id.find("dl")
        the_id = id_group.find("span")

        id_ = the_id.text
        # Gets rid of a newline character on scraped ID
        id_ = id_.strip()
        print id_

    unscraped_descrip = soup.find_all("div", "iCIMS_InfoMsg iCIMS_InfoMsg_Job")

    for pos in unscraped_descrip:
        descrip_group = pos.find("p")
        descrip = descrip_group.text
        print descrip
        break

    # Adds a row in Database
    time = banner_server.get_date_from_id(id_, get_current_date())

    time = time.strftime("%d-%b-%y")

    return [id_, descrip, title, time, link]


def get_current_date():
    time = datetime.datetime.now().strftime("%d-%b-%y")
    return time
