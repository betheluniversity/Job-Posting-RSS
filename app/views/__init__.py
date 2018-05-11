import requests
import datetime

from flask import render_template, make_response
from flask.ext.classy import FlaskView, route
from bs4 import BeautifulSoup

from app import app
from app.banner import Banner
from app.basic_auth import *


class JobRSSView(FlaskView):

    def __init__(self):
        # Banner Connection
        self.banner_server = Banner()

    @route("/")
    def index(self):
        file = open(app.config['INSTALL_LOCATION'] + '/news-campaign.rss', "r")
        response = make_response(file.read())
        response.headers["Content-Type"] = "application/xml"
        file.close()
        return response

    @route("/create_new_rss")
    @requires_auth
    def create_new_rss(self):
        # Uses Requests to grab the xml
        xml = requests.get(app.config['STAFF_SCRAPE_URL'], params=None)
        # Creates soup from bs4
        # TODO think about changing to a faster parser
        soup = BeautifulSoup(xml.text, "html.parser")
        # Loops through all links in XML, notated by the <loc> tag
        number = 0
        jobs = []
        # TODO Maybe force all commits to happen at once. (versus each loop)
        # For above change to be made, you will need to introduce the banner_server commit, etc., into __init__.py class
        for link in soup.find_all('loc'):
            jobs.append(self._page_scrape(link.get_text()))
            number = number + 1

        feed_date = datetime.datetime.now().strftime('%a, %d %b %Y')

        # return "Scraped from %s Job Listings." % number
        sitemap_xml = render_template('output.xml', **locals())
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        file = open(app.config['INSTALL_LOCATION'] + '/news-campaign.rss', "wr")
        file.write(sitemap_xml.encode('utf-8'))
        file.close()
        return response

    def _get_iframe_link(self, link):
        webpage = requests.get(link, params=None)
        soup = BeautifulSoup(webpage.text, 'html.parser')
        element = soup.find("iframe")
        link = element["src"]
        return link

    def _page_scrape(self, link):
        # Variables needed to Scrape
        iframe_link = self._get_iframe_link(link)
        webpage = requests.get(iframe_link, params=None)
        soup = BeautifulSoup(webpage.text, 'html.parser')

        # Data the program is finding
        id_ = ""
        descrip = ""
        title = soup.find("h1").text.strip()

        unscraped_id = soup.find_all("div", "iCIMS_JobHeaderGroup")

        for group_with_id in unscraped_id:
            # Should only have to loop once
            id_group = group_with_id.find("dl")
            the_id = id_group.find("span")

            id_ = the_id.text
            # Gets rid of a newline character on scraped ID
            id_ = id_.strip()

        unscraped_descrip = soup.find_all("div", "iCIMS_InfoMsg iCIMS_InfoMsg_Job")

        for pos in unscraped_descrip:
            descrip_group = pos.find("p")
            descrip = descrip_group.text
            break

        # Adds a row in Database
        time = self.banner_server.get_date_from_id(id_, self._get_current_date())

        time = time.strftime('%a, %d %b %Y')

        return [id_, descrip, title, time, link]

    def _get_current_date(self):
        time = datetime.datetime.now().strftime("%d-%b-%y")
        return time
