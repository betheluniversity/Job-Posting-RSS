import requests
import datetime

from flask import render_template, make_response
from flask_classy import FlaskView, route
from bs4 import BeautifulSoup

from app import app
from app.basic_auth import *


class JobRSSView(FlaskView):

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
        soup = BeautifulSoup(xml.text, "html.parser")

        number = 0
        jobs = []

        # Loops through all links in XML, notated by the <loc> tag
        for link in soup.find_all('loc'):
            if '/jobs/search' not in link.get_text():
                jobs.append(self._scrape_job(link.get_text()))
                number = number + 1

        jobs.sort(key=lambda i: i['sort-date'])

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

    def _scrape_job(self, link):
        # Variables needed to Scrape
        iframe_link = self._get_iframe_link(link)
        webpage = requests.get(iframe_link, params=None)
        soup = BeautifulSoup(webpage.text, 'html.parser')

        title = soup.find("h1").text.strip()

        try:
            date = soup.find(text='Posted Date').parent.findNext('span').attrs['title'].split(' ')[0]
            date = datetime.datetime.strptime(date, '%m/%d/%Y')
        except:
            date = datetime.datetime.now()

        job_id = ""
        unscraped_id = soup.find_all("div", "iCIMS_JobHeaderGroup")
        for group_with_id in unscraped_id:
            # Should only have to loop once
            id_group = group_with_id.find("dl")

            # Gets rid of a newline character on scraped ID
            job_id = id_group.find("span").text.strip()

        desc = ""
        unscraped_desc = soup.find_all("div", "iCIMS_InfoMsg iCIMS_InfoMsg_Job")
        for pos in unscraped_desc:
            desc_group = pos.find("p")
            # if the paragraph doesn't work, try li.
            if not desc_group:
                desc_group = pos.find("li")
            desc = desc_group.text
            break

        return {
            'link': link,
            'title': title,
            'date': datetime.datetime.strftime(date, '%a, %d %b %Y'),
            'sort-date': date,
            'id': job_id,
            'desc': desc
        }

    def _get_current_date(self):
        time = datetime.datetime.now().strftime("%d-%b-%y")
        return time
