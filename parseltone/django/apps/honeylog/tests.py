"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

"""

from django.test import TestCase
from models import HoneyLog
from views import log_post


class SimpleTest(TestCase):
    def test_store_dict(self):
        """

        Standard set of arguments from a python http log handler

        threadName=MainThread
        created=1321900393.38
        process=31935
        processName=MainProcess
        args=%28%29
        module=%3Cipython-input-17-4591a35af528%3E
        filename=%3Cipython-input-17-4591a35af528%3E
        levelno=40
        exc_text=None
        pathname=%3Cipython-input-17-4591a35af528%3E
        lineno=1
        msg=burning
        exc_info=None
        funcName=%3Cmodule%3E
        relativeCreated=325542951.63
        levelname=ERROR
        msecs=379.678010941
        """
        test_dict = dict(
            args="%28%29",
            created=1321900393.38,
            filename="%3Cipython-input-17-4591a35af528%3E",
            funcName="%3Cmodule%3E",
            levelname="ERROR",
            levelno=40,
            lineno=1,
            module="%3Cipython-input-17-4591a35af528%3E",
            msecs=379.678010941,
            msg="burning",
            pathname="%3Cipython-input-17-4591a35af528%3E",
            process=31935,
            processName="MainProcess",
            relativeCreated=325542951.63,
            threadName="MainThread",
        )
        h = HoneyLog(**test_dict)
        h.save()
        print(h)
