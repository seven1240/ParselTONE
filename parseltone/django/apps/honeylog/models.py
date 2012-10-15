"""
Model incoming logs
"""

from django.db import models

# Create your models here.

class HoneyLog(models.Model):
    """
    Store python 2.7 std lib style logs

    Ought to mimic the python standard library (v2.7.2) LogRecord object
    attribute names. (but not all the attributes necessarily.)

    Does not store exc_info (sys.exc_info() outputs tuple of (type, value, traceback)
    nor args.

    msg is assumed to be the formatted result of LogRecord.msg and LogRecord.args

    Do not use custom logging levels (stick with the standard 5).
    """

#    Standard debug encodings
#    DEBUG_LEVEL_CHOICES = (
#        (10, 'Debug',),
#        (20, 'Info',),
#        (30, 'Warn',),
#        (40, 'Error',),
#        (50, 'Critical',),
#    )

    args = models.TextField("serialization of the arguments to a function. Potentially extremely verbose")
    created = models.DecimalField(max_digits=20, decimal_places=5)
    filename = models.CharField(max_length=255)
    funcName = models.CharField(max_length=255)
    levelname = models.CharField(max_length=255)
    levelno = models.IntegerField()
    lineno = models.IntegerField()
    module = models.CharField(max_length=255)
    msecs = models.DecimalField(max_digits=20, decimal_places=5)
    msg = models.TextField(help_text="The rendered log message. May be quite" " long. In contrast to the stdlib LogRecord object," " this is the combination of LogRecord.msg and" " LogRecord.args")
    name = models.CharField(max_length=255)
    pathname = models.CharField(max_length=255)
    process = models.IntegerField()
    processName = models.CharField(max_length=255)
    relativeCreated = models.DecimalField(max_digits=20, decimal_places=5)
    threadName = models.CharField(max_length=255)

    # record keeping, may also be helpful for windows systems
    record_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{s.created}: {s.name}: {s.levelno} {s.levelname}: {s.msg}".format(s=self)
