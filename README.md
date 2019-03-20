# Job-Posting-RSS
Site grabs data from Job Posting Bethel Site, and scrapes each link for data. Then turns the data into an RSS feed. This RSS feed is then processed by Campaign Monitor to send out emails when it changes.

![alt text](https://www.lucidchart.com/publicSegments/view/a7dc2e7a-26c0-4105-828e-f949cefedef9/image.png)

If the Diagram needs to be changed: [LucidChart Diagram Edit Link](https://www.lucidchart.com/invitations/accept/61b1a9e1-f640-46eb-8bd5-c8c8200d30e5)

To Create Table in Database:
```sql
CREATE TABLE JOB_POST_RSS
(
JOB_ID VARCHAR2(12 CHAR),
DATE_FOUND DATE,
DATE_LAST_SEEN DATE
);
```
