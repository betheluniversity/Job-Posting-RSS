import datetime
from email import utils

import requests
from bs4 import BeautifulSoup
from flask import render_template, make_response, request
from flask_classy import FlaskView, route

from app import app
from app.basic_auth import requires_auth


class JobRSSView(FlaskView):

    @route("/staff")
    @route("/faculty")
    @route("/both")
    @route("/")
    def index(self):
        if 'staff' in request.path:
            rss_name = 'staff.rss'
        elif 'faculty' in request.path:
            rss_name = 'faculty.rss'
        else:
            rss_name = 'both.rss'

        file = open(app.config['INSTALL_LOCATION'] + '/app/rss/' + rss_name, "rb")
        response = make_response(file.read())
        response.headers["Content-Type"] = "application/xml"
        file.close()
        return response

    @requires_auth
    @route("/create_new_rss")
    def create_new_rss(self):
        scrape_objects = [
            {
                'rss-name': 'staff.rss',
                'scrape-url': app.config['STAFF_SCRAPE_URL'],
                'title': 'Bethel University Staff Openings',
                'description': 'A listing of the current staff openings at Bethel University',
                'jobs-url': 'https://staffcareers-bethel.icims.com/jobs/search'
            },
            {
                'rss-name': 'faculty.rss',
                'scrape-url': app.config['FACULTY_SCRAPE_URL'],
                'title': 'Bethel University Faculty Openings',
                'description': 'A listing of the current faculty openings at Bethel University',
                'jobs-url': 'https://facultycareers-bethel.icims.com/jobs/search'
            }
        ]
        all_jobs_list = []
        for scrape_object in scrape_objects:
            # Uses Requests to grab the xml
            xml = requests.get(scrape_object.get('scrape-url'), params=None)

            # Creates soup from bs4
            soup = BeautifulSoup(xml.text, "html.parser")

            jobs = []
            # Loops through all links in XML, notated by the <loc> tag
            for link in soup.find_all('loc'):
                if '/jobs/search' not in link.get_text():
                    job = self._scrape_job(link.get_text())
                    jobs.append(job)
                    all_jobs_list.append(job)

            jobs.sort(key=lambda i: i['sort-date'])

            self._make_rss(jobs, scrape_object)

        # sort the all_jobs_list
        all_jobs_list.sort(key=lambda i: i['sort-date'])
        all_jobs_scrape_object = {
            'rss-name': 'both.rss',
            'scrape-url': None,
            'title': 'Bethel University Staff and Faculty Openings',
            'description': 'A listing of the current staff and faculty openings at Bethel University',
            'jobs-url': 'https://www.bethel.edu/employment/'
        }
        self._make_rss(all_jobs_list, all_jobs_scrape_object)
        return 'success'

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
            now = datetime.datetime.now()
            date = date.replace(hour=now.hour, minute=now.minute, second=now.second)
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
            'date': utils.format_datetime(date),
            'sort-date': date,
            'id': job_id,
            'desc': desc
        }

    def _get_current_date(self):
        time = datetime.datetime.now().strftime("%d-%b-%y")
        return time

    def _make_rss(self, jobs, scrape_objects):
        feed_date = utils.format_datetime(datetime.datetime.now())

        sitemap_xml = render_template('output.xml', **locals())
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"

        file = open(app.config['INSTALL_LOCATION'] + '/app/rss/' + scrape_objects.get('rss-name'), "wb")
        file.write(sitemap_xml.encode('utf-8'))
        file.close()
