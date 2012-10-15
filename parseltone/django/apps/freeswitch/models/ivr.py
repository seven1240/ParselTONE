from django.db import models
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy


def truncate_letters(s, num, end_text='...'):
    """Truncates a string after a certain number of letters. Takes an optional
    argument of what should be used to notify that the string has been
    truncated, defaulting to ellipsis (...)

    Newlines in the string will be stripped.
    
    Heavily borrowed from the django truncate_words() method:
    https://code.djangoproject.com/browser/django/tags/releases/1.3/django/utils/text.py#L39
    """
    s = force_unicode(s)
    length = int(num)
    text = s.strip().replace('\n', '').replace('\r', '')
    if len(text) > length:
        text = text[:length]
        if not text[-1].endswith(end_text):
            text += end_text
    return text
truncate_letters = allow_lazy(truncate_letters, unicode)


class IVRMenu(models.Model):
    """
    http://wiki.freeswitch.org/wiki/Misc._Dialplan_Tools_ivr
    """
    name = models.CharField(max_length=64)
    greet_long = models.CharField(max_length=128, # TODO: use filefield? but certain strings are also valid..
        help_text="The prompt played the first time the menu is played. "
            "May be a filename (starting with \ or /) or 'say:Text to speak' "
            "for TTS, or 'phrase: phrase_macro_name' to speak a phrase macro.")
    greet_short = models.CharField(max_length=128, # TODO: use filefield? but certain strings are also valid..
        help_text="A shorter version of the prompt played when the menu loops. "
            "May be a filename (starting with \ or /) or 'say:Text to speak' "
            "for TTS, or 'phrase: phrase_macro_name' to speak a phrase macro.")
    invalid_sound = models.CharField(max_length=128, # TODO: use filefield? but certain strings are also valid..
        help_text="Played when no entry or an invalid entry is made. "
            "May be a filename (starting with \ or /) or 'say:Text to speak' "
            "for TTS, or 'phrase: phrase_macro_name' to speak a phrase macro.")
    exit_sound = models.CharField(max_length=128, # TODO: use filefield? but certain strings are also valid..
        help_text="Played when the menu is terminated. "
            "May be a filename (starting with \ or /) or 'say:Text to speak' "
            "for TTS, or 'phrase: phrase_macro_name' to speak a phrase macro.")
    inter_digit_timeout = models.IntegerField(default=4000,
        help_text="Number of milliseconds to wait for a selection.")
    timeout = models.IntegerField(default=2000,
        help_text="Number of milliseconds to wait after playing confirm-macro "
            "to confirm entered digits.")
    #confirm_key = # TODO: no details in wiki
    #confirm_attempts = # TODO: no details in wiki
    max_failures = models.IntegerField(default=3, 
        help_text="Maximum number of failures before ending the menu.")
    tts_engine = models.CharField(max_length=64, blank=True,
        help_text="Name of TTS engine to speak text (ie: cepstral).")
    tts_voice = models.CharField(max_length=64, blank=True,
        help_text="Name of TTS voice to use to speak text (ie: david).")
    phrase_lang = models.CharField(max_length=64, blank=True,
        help_text="Override language to use. Will override the "
            "default_language channel variable.")
    # digit_len = # TODO: no details in wiki
    actions = models.ManyToManyField('freeswitch.IVRMenuAction')

    class Meta:
        app_label = 'freeswitch'
        verbose_name = 'IVR menu'
        verbose_name_plural = 'IVR menus'

    def __unicode__(self):
        return self.name


class IVRMenuAction(models.Model):
    digits = models.CharField(max_length=12)
    action = models.CharField(max_length=24, default='exec-app', choices = (
            ('play', 'Play a sound file'),
            ('tts', 'Speak text'),
            ('exec', 'Execute a FreeSWITCH dialplan application'),
            ('sub', 'Enter another menu'),
            ('back', 'Return to prior menu'),
            ('top', 'Return to first menu'),
            ('exit', 'Exit the IVR'),
        ))
    parameters = models.TextField(blank=True)

    class Meta:
        app_label = 'freeswitch'
        ordering = ('digits',)
        verbose_name = 'IVR menu action'
        verbose_name_plural = 'IVR menu actions'

    def __unicode__(self):
        return '{digits}: {action:>4} {parameters}'.format(
            digits = self.digits,
            action = self.action.upper(),
            parameters = truncate_letters(self.parameters, 30),
        )

