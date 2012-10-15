# Create your views here.

from parseltone.django.apps.honeylog.models import HoneyLog

def log_post(request):
    """
    Record logs submitted by the standard python logging.handlers.HTTPHandler

    No checking on data beyond what django does in constructing the model

    Typical Python HTTPLogger post:

        args=%28%29
        created=1321900393.38
        exc_info=None
        exc_text=None
        filename=%3Cipython-input-17-4591a35af528%3E
        funcName=%3Cmodule%3E
        levelname=ERROR
        levelno=40
        lineno=1
        module=%3Cipython-input-17-4591a35af528%3E
        msecs=379.678010941
        msg=burning
        pathname=%3Cipython-input-17-4591a35af528%3E
        process=31935
        processName=MainProcess
        relativeCreated=325542951.63
        threadName=MainThread

    Honey log does not necessarily take all of these arguments

    """

    if not request.method == 'POST':
        return

    fields = ['args', 'created', 'filename', 'funcName', 'levelname',
              'levelno', 'lineno', 'module', 'msecs', 'msg', 'name',
              'pathname', 'process', 'processName', 'relativeCreated',
              'threadName',]

    args = {f: request.POST[f] for f in fields}

    HoneyLog.objects.create(**args)
