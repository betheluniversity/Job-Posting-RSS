__author__ = ['ejc84332', 'grg27487']
# python
import sqlalchemy
import datetime
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

# local
from config import DB_KEY, CONSTR
import cx_Oracle


class Banner():

    def __init__(self):
        self.engine, self.metadata, self.session = self.get_connection()
        # Am I going to get into trouble for re-using these cursors?
        self.call_cursor, self.result_cursor = self.get_cursor_connection()

    def get_cursor_connection(self):
        conn = self.engine.raw_connection()
        # Get a cursor to call the procedure and a cursor to store the results.
        call_cursor = conn.cursor()
        result_cursor = conn.cursor()
        return call_cursor, result_cursor

    def get_connection(self):
        # Login

        constr = CONSTR % DB_KEY

        engine = sqlalchemy.create_engine(constr, echo=True)

        metadata = MetaData(engine)
        session = sessionmaker(bind=engine)()

        return engine, metadata, session

    def execute(self, sql):
        result = self.session.execute(sql)
        self.session.commit()
        return result

    # Determines if the Table contains a row with the JOB_ID of job_id
    # Also returns the Date for that ID
    def get_date_from_id(self, job_id, date_):
        sql = """SELECT DATE_FOUND FROM JOB_POST_RSS WHERE JOB_ID = '%s'""" % job_id
        results = self.session.execute(sql)
        # Gets the Row of Data
        result = results.fetchone()

        if result is None:
            self.session.commit()
            self.insert_row(job_id, date_)
            date_ = datetime.datetime.strptime(date_, "%d-%b-%y")
            return date_

        result = result.items()[0][1]
        # self.session.commit()

        sql = """UPDATE JOB_POST_RSS SET DATE_LAST_SEEN='%s' WHERE JOB_ID='%s'""" % (date_, job_id)
        # self.session.execute(sql)
        # self.session.commit()
        self.execute(sql)
        # result will be a datetime Object
        return result

    # Inserts row with the Job_id, and the Current Date
    def insert_row(self, id_, date_):
        sql = """INSERT INTO JOB_POST_RSS VALUES ('%s','%s','%s')""" % (id_, date_, date_)
        results = self.execute(sql)
        return results
