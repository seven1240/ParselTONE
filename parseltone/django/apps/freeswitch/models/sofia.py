from django.db import models
from parseltone.django.apps.freeswitch import fields


class SofiaGlobalSettings(models.Model):
    freeswitch_server = models.OneToOneField('freeswitch.FreeswitchServer')
    log_level = models.IntegerField(default=0)
    auto_restart = models.BooleanField()
    debug_presence = models.IntegerField(default=0)

    class Meta:
        app_label = 'freeswitch'
        verbose_name_plural = 'Sofia global settings'

    def __unicode__(self):
        return unicode(self.freeswitch_server)


class SofiaDomain(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32)
    address = fields.FSIPAddressField()
    dial_string = models.CharField(max_length=256,
        default="{sip_invite_domain=${dialed_domain},"
        "presence_id=${dialed_user}@${dialed_domain}}$"
        "{sofia_contact(${dialed_user}@${dialed_domain})}")
    record_stereo = models.BooleanField(default=True)
    default_gateway = models.ForeignKey('freeswitch.SofiaGateway',
        null=True, blank=True)
    default_areacode = models.IntegerField(null=True, blank=True)
    transfer_fallback_extension = models.ForeignKey(
        'freeswitch.SofiaExtension', null=True, blank=True)

    class Meta:
        app_label = 'freeswitch'

    def __unicode__(self):
        return unicode(self.name)


class SofiaProfile(models.Model):
    freeswitch_server = models.ForeignKey('freeswitch.FreeswitchServer')
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=32)
    aliases = models.CharField(max_length=128,
        help_text="Other names that will work as a valid profile name "
        "for this profile.")
    domain = models.ForeignKey('freeswitch.SofiaDomain')
    resume_media_on_hold = models.BooleanField(
        help_text="When calls are in no media this will bring them back to "
        "media when you press the hold button.")
    bypass_media_after_att_xfer = models.BooleanField(
        help_text="This will allow a call after an attended transfer go "
        "back to bypass media after an attended transfer.")
    user_agent_string = models.CharField(max_length=32,
        default="I <3 Parseltone!")
    debug = models.IntegerField(default=0)
    shutdown_on_fail = models.BooleanField(
        help_text="Shutdown FreeSWITCH if this profile fails to load.")
    sip_trace = models.BooleanField()
    liberal_dtmf = models.BooleanField(default=True,
        help_text="Don't be picky about negotiated DTMF just always offer "
        "2833 and accept both 2833 and INFO.")
    watchdog_enabled = models.BooleanField(verbose_name="Use watchdog")
    watchdog_step_timeout = models.IntegerField(default=30000,
        verbose_name="Step timeout")
    watchdog_event_timeout = models.IntegerField(default=30000,
        verbose_name="Event timeout")
    log_auth_failures = models.BooleanField(default=True)
    forward_unsolicited_mwi_notify = models.BooleanField()
    context = models.CharField(max_length=32, default="public")
    # see http://freeswitch-users.2379917.n2.nabble.com/rfc2833-pt-td6317163.html
    ## for discussion about the value for rfc2833_pt
    rfc2833_pt = models.IntegerField(default=101)
    sip_port = fields.FSIntegerField(default="$${internal_sip_port}",
        help_text="Port to bind to for SIP traffic.")
    dialplan = models.CharField(max_length=10, default='xml', choices=(
        ('xml', 'XML'), # TODO: what are the other choices?
    ))
    dtmf_duration = models.IntegerField(default=2000)
    inbound_codec_prefs = models.TextField(default="$${global_codec_prefs}")
    outbound_codec_prefs = models.TextField(default="$${global_codec_prefs}")
    rtp_timer_name = models.CharField(max_length=32, default="soft")
    rtp_ip = fields.FSIPAddressField(default="$${local_ip_v4}")
    sip_ip = fields.FSIPAddressField(default="$${local_ip_v4}")
    hold_music = models.CharField(max_length=64, default="$${hold_music}")
    apply_nat_acl = models.ForeignKey('freeswitch.ACL',
        null=True, blank=True,
        related_name='sofia_profile_nat_acl_set')
    cid_in_1xx = models.BooleanField(default=True,
        help_text="Set to false if you do not wish to have called party "
        "info in 1XX responses.")
    extended_info_parsing = models.BooleanField() # TODO: should this be default true?
    aggressive_nat_detection = models.BooleanField() # TODO: should this be default true?
    enable_100rel = models.BooleanField(
        help_text="There are known issues (asserts and segfaults) when "
        "100rel is enabled. It is not recommended to enable 100rel at "
        "this time.")
    enable_compact_headers = models.BooleanField(
        help_text="Enable Compact SIP headers.")
    enable_timer = models.BooleanField(
        help_text="Enable/disable session timers.")
    minimum_session_expires = models.IntegerField(default=120)
    apply_inbound_acl = models.ForeignKey('freeswitch.ACL',
        null=True, blank=True,
        related_name='sofia_profile_inbound_acl_set')
    local_network_acl = models.ForeignKey('freeswitch.ACL',
        null=True, blank=True,
        related_name='sofia_profile_network_acl_set')
    apply_register_acl = models.ForeignKey('freeswitch.ACL',
        null=True, blank=True,
        verbose_name="Registration ACL",
        related_name='sofia_profile_register_acl_set')
    dtmf_type = models.CharField(max_length=7, default='rfc2833', choices=(
        ('info', 'INFO'), ('rfc2833', 'RFC-2833')
    ))
    send_message_query_on_register = models.BooleanField(
        help_text="Only on the first register, or every time?")
    send_presence_on_register = models.BooleanField(
        help_text="Only on the first register, or every time?")
    caller_id_type = models.CharField(max_length=4, blank=True,
        choices=(
            ('rpid', 'rpid'), ('pid', 'pid')
        ), help_text="Caller-ID type (can be overridden by inbound call "
        "type and/or sip_cid_type channel variable.")
    record_path = models.CharField(max_length=64) # TODO: filepath or var
    record_template = models.CharField(max_length=128,
        default="${caller_id_number}.${target_domain}"
        ".${strftime(%Y-%m-%d-%H-%M-%S)}.wav")
    manage_presence = models.BooleanField(help_text="Enable to use presence.")
    presence_probe_on_register = models.BooleanField(
        help_text="Send a presence probe on each register to query devices to "
        "send presence instead of sending presence with less info.")
    manage_shared_presence = models.BooleanField()
    dbname = models.CharField(max_length=64, default="share_presence",
        help_text="Used to share presence info across sofia profiles. "
        "Name of the db to use for this profile.")
    presence_hosts = models.CharField(max_length=64,
        default="$${domain},$${local_ip_v4}")
    bitpacking = models.CharField(max_length=4, blank=True,
        choices=(('aal2', 'AAl2'),), help_text="AAL2 bitpacking on G.726")
    max_proceeding = models.IntegerField(default=1000,
        help_text="Max number of open dialogs in proceeding.")
    session_timeout = models.IntegerField(default=1800,
        help_text="Session timers for all calls to expire after "
        "the specified seconds.")
    multiple_registrations = models.BooleanField()
    inbound_codec_negotiation = models.CharField(max_length=8,
        default='generous', choices=(
            ('generous', "Equally consider remote and local precedence lists."),
            ('greedy', "Force local precedence."),
            ('scrooge', "Remote precedence list is ignored completely."),
        ))
    bind_params = models.CharField(max_length=64, blank=True,
        help_text="If you want to send any special bind params of your own.")
    unregister_on_options_fail = models.BooleanField()
    tls = models.BooleanField(verbose_name="Use TLS")
    tls_bind_params = models.CharField(max_length=64, blank=True,
        verbose_name="Bind params", default="transport=tls",
        help_text="Additional bind parameters for TLS.")
    tls_sip_port = fields.FSIntegerField(default=5061,
        verbose_name="SIP port",
        help_text="Port to listen on for TLS requests.")
    tls_cert_dir = models.CharField(max_length=128, blank=True,
        verbose_name="Certificate directory",
        help_text="Location of the agent.pem and cafile.pem SSL certificates.")
    tls_version = models.CharField(max_length=32, default='sslv23',
        verbose_name="Version", choices=(
            ('sslv23', 'SSLv23'), ('tlsv1', 'TLSv1'),
        ), help_text="NOTE: Phones may not work with TLSv1")
    rtp_autoflush_during_bridge = models.BooleanField(
        help_text="Turn on auto-flush during bridge (skip timer sleep when "
        "the socket already has data) (reduces delay on latent connections "
        "default true, must be disabled explicitly)")
    rtp_rewrite_timestamps = models.BooleanField(
        help_text="If you don't want to pass through timestamps from 1 RTP "
        "call to another (on a per call basis with rtp_rewrite_timestamps "
        "chanvar)")
    pass_rfc2833 = models.BooleanField()
    odbc_dsn = models.CharField(max_length=64, blank=True,
        help_text="If you have ODBC support and a working dsn you can use "
        "it instead of SQLite. (ex: dsn:user:pass)")
    inbound_bypass_media = models.BooleanField(
        help_text="Set all inbound calls to no media mode.")
    inbound_proxy_media = models.BooleanField(
        help_text="Set all inbound calls to proxy media mode.")
    inbound_late_negotiation = models.BooleanField(
        help_text="Let calls hit the dialplan *before* deciding if the "
        "codec is ok.")
    accept_blind_reg = models.BooleanField(help_text="Let anything register.")
    accept_blind_auth = models.BooleanField(
        help_text="Accept any authentication without actually checking "
        "(not a good feature for most people).")
    suppress_cng = models.BooleanField(
        help_text="Suppress CNG on this profile.")
    nonce_ttl = models.IntegerField(default=60,
        help_text="TTL for nonce in SIP auth.")
    disable_transcoding = models.BooleanField(
        help_text="Force the outbound leg of a bridge to only offer the "
        "codec that the originator is using.")
    manual_redirect = models.BooleanField(
        help_text="Handle 302 redirect in the dialplan.")
    disable_transfer = models.BooleanField()
    disable_register = models.BooleanField()
    ndlb_broken_auth_has = models.BooleanField(
        help_text="Used for when phones respond to a challenged ACK with "
        "method INVITE in the hash.")
    ndlb_received_in_nat_reg_contact = models.BooleanField(
        help_text='Add a ;received="<ip>:<port>" to the contact when '
        'replying to register for nat handling.')
    auth_calls = models.BooleanField()
    inbound_reg_force_matching_username = models.BooleanField(
        help_text="Force the user and auth-user to match.")
    auth_all_packets = models.BooleanField(
        help_text="On authed calls, authenticate *all* the packets not "
        "just invite.")
    ext_rtp_ip = models.CharField(max_length=32, default='auto-nat',
        help_text="Used as the public IP address for SDP. Can be an one "
        "of: ip address ('12.34.56.78'), a stun server lookup "
        "('stun:stun.server.com'), a DNS name ('host:host.server.com'), "
        "auto (use guessed ip), auto-nat (use ip learned from NAT-PMP or "
        "UPNP)")
    ext_sip_ip = models.CharField(max_length=32, default='auto-nat',
        help_text="Used as the public IP address for SDP. Can be an one "
        "of: ip address ('12.34.56.78'), a stun server lookup "
        "('stun:stun.server.com'), a DNS name ('host:host.server.com'), "
        "auto (use guessed ip), auto-nat (use ip learned from NAT-PMP or "
        "UPNP)")
    rtp_timeout_sec = models.IntegerField(default=300)
    rtp_hold_timeout_sec = models.IntegerField(default=1800)
    vad = models.CharField(max_length=4, default='out', choices=(
        ('in', 'IN'), ('out', 'OUT'), ('both', 'BOTH')
    ))
    alias = models.CharField(max_length=64, blank=True,
        help_text="ex: sip:10.0.1.251:5555")
    force_register_domain = fields.FSIPAddressField(default='$${domain}',
        help_text="All inbound reg will look in this domain for the users.")
    force_subscription_domain = fields.FSIPAddressField(default='$${domain}',
        help_text="Force the domain in subscriptions to this value.")
    force_register_db_domain = fields.FSIPAddressField(default='$${domain}',
        help_text="All inbound reg will stored in the db using this domain.")
    delete_subs_on_register = models.BooleanField()
    rtcp_audio_passthrough = models.BooleanField(
        help_text="Enable rtcp on every channel also can be done per leg "
        "basis to pass it across a call.")
    rtcp_audio_interval_msec = models.IntegerField(default=5000)
    rtcp_video_interval_msec = models.IntegerField(default=5000)
    force_subscription_expires = models.IntegerField(blank=True, null=True,
        help_text="Force suscription expires to a lower value than requested.")
    disable_transfer = models.BooleanField(
        help_text="Disable transfer which may be undesirable "
        "in a public switch.")
    disable_register = models.BooleanField(
        help_text="Disable register which may be undesirable "
        "in a public switch.")
    enable_3pcc = models.CharField(max_length=5, blank=True, choices=(
        ('true', 'Accept immediately'), ('proxy', 'Wait for answer')
    ))
    ndlb_force_rport = models.BooleanField(
        help_text="Use at your own risk, or if you know what this does.")
    challenge_realm = models.CharField(max_length=64, default='auto_to',
        blank=True, null=True,
        help_text="Choose the realm challenge key. Default is 'auto_to' if "
        "not set. Set to 'auto_from' to use the from field as the value for "
        "the sip realm. Set to 'auto_to' to use the to field as the value "
        "for the sip realm. Otherwise, you can input any value to use for the "
        "sip realm. If you want URL dialing to work you'll want to set this "
        "to 'auto_from'. (If you use any other value besides 'auto_to' or "
        "'auto_from' you'll lose the ability to do multiple domains.)\n"
        "Note: comment out to restore the behavior before 2008-09-29.")
    disable_rtp_auto_adjust = models.BooleanField()
    inbound_use_callid_as_uuid = models.BooleanField(
        help_text="On inbound calls make the uuid of the session equal to "
        "the sip call id of that call.")
    outbound_use_callid_as_uuid = models.BooleanField(
        help_text="On outbound calls set the callid to match the uuid of "
        "the session.")
    rtp_autofix_timing = models.BooleanField(default=True)
    pass_callee_id = models.BooleanField(default=True,
        help_text="Set this param to false if your gateway for some reason "
        "hates X- headers that it is supposed to ignore.")
    auto_rtp_bugs = models.TextField(blank=True,
        help_text="Value 'clear' clears them all or supply the name to add "
        "or the name prefixed with ~ to remove. Valid values: clear, "
        "CISCO_SKIP_MARK_BIT_2833, SONUS_SEND_INVALID_TIMESTAMP_2833")
    disable_srv = models.BooleanField(default=True,
        help_text="Can be used as workaround with bogus SRV records.")
    disable_naptr = models.BooleanField(default=True,
        help_text="Can be used as workaround with bogus NAPTR records.")
    timer_t1 = models.IntegerField(default=500,
        help_text="Set the T1 retransmission interval used by the SIP "
        "transaction engine. The T1 is the initial duration used by "
        "request retransmission timers A and E (UDP) as well as response "
        "retransmission timer G.")
    timer_t1x64 = models.IntegerField(default=32000,
        help_text="Set the T1x64 timeout value used by the SIP transaction "
        "engine. The T1x64 is duration used for timers B, F, H, and J (UDP) "
        "by the SIP transaction engine. The timeout value T1x64 can be "
        "adjusted separately from the initial retransmission interval T1.")
    timer_t2 = models.IntegerField(default=4000,
        help_text="Set the maximum retransmission interval used by the SIP "
        "transaction engine. The T2 is the maximum duration used for the "
        "timers E (UDP) and G by the SIP transaction engine. Note that the "
        "timer A is not capped by T2. Retransmission interval of INVITE "
        "requests grows exponentially until the timer B fires.")
    timer_t4 = models.IntegerField(default=4000,
        help_text="Set the lifetime for completed transactions used by the "
        "SIP transaction engine. A completed transaction is kept around for "
        "the duration of T4 in order to catch late responses. The T4 is the "
        "maximum duration for the messages to stay in the network and the "
        "duration of SIP timer K.")
    auto_jitterbuffer_msec = models.IntegerField(default=0,
        help_text="Turn on a jitterbuffer for every call.")
    renegotiate_codec_on_hold = models.BooleanField(
        help_text="By default mod_sofia will ignore the codecs in the sdp "
        "for hold/unhold operations. Set this to true if you want to "
        "actually parse the sdp and re-negotiate the codec during "
        "hold/unhold. It's probably not what you want so stick with the "
        "default unless you really need to change this.")

    class Meta:
        app_label = 'freeswitch'

    def __unicode__(self):
        return self.name

    def clean(self):
        if not self.tls_sip_port:
            self.tls_sip_port = 5061
        if self.timer_t1 and not self.timer_t1x64:
            self.timer_t1x64 = self.timer_t1 * 64

    def get_extension_dial_string(self, extension):
        if extension not in self.sofiaextension_set.all():
            raise ValueError('Extension not related to this profile.')
        return 'sofia/{name}/{extname}@{domain}'.format(
            name=self.slug, extname=extension.register_username,
            domain=self.domain.address)


class SofiaGateway(models.Model):
    name = models.CharField(max_length=64)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    realm = models.CharField(max_length=64, blank=True,
        help_text="Same as name, if blank.")
    from_user = models.CharField(max_length=64, blank=True,
        help_text="Same as username, if blank.")
    from_domain = models.CharField(max_length=64, blank=True,
        help_text="Same as realm, if blank.")
    extension = models.CharField(max_length=64, blank=True,
        help_text="Extension for inbound calls; same as username, if blank.")
    proxy = models.CharField(max_length=64, blank=True,
        help_text="Proxy host; same as realm, if blank.")
    register_proxy = models.CharField(max_length=64, blank=True,
        help_text="Send register to this proxy; same as proxy, if blank.")
    expire_seconds = models.IntegerField(default=3600)
    register = models.BooleanField()
    register_transport = models.CharField(max_length=3, default='udb',
        choices=(('udp', 'UDP'),), # TODO: what are the other values? TCP?
        help_text="Which transport to use for register.")
    retry_seconds = models.IntegerField(default=30,
        help_text="How many seconds before a retry when a failure or "
        "timeout occurs.")
    caller_id_in_from = models.BooleanField(
        help_text="Use the callerid of an inbound call in the from field "
        "on outbound calls via this gateway.")
    # TODO: FS sample xml has example value for contact_params set to
    ## 'tport=tcp' - is that meant to be a default, or just an example?
    contact_params = models.TextField(blank=True,
        help_text="Extra SIP params to send in the contact.")
    ping = models.IntegerField(default=25,
        help_text="Send an options ping every N seconds, failure will "
        "unregister and/or mark it down.")

    class Meta:
        app_label = 'freeswitch'

    def clean(self):
        if not self.realm:
            self.realm = self.name
        if not self.from_user:
            self.from_user = self.username
        if not self.from_domain:
            self.from_domain = self.realm
        if not self.extension:
            self.extension = self.username
        if not self.proxy:
            self.proxy = self.realm
        if not self.register_proxy:
            self.register_proxy = self.proxy
        if not self.expire_seconds:
            self.expire_seconds = 3600
        if not self.ping:
            self.ping = 25


class SofiaPhone(models.Model):
    mac_address = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=64)
    last_config_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'freeswitch'

    def __unicode__(self):
        return self.name


class SofiaExtension(models.Model):
    """
    A single extension.
    """
    name = models.CharField(max_length=32)
    phone = models.ForeignKey('freeswitch.SofiaPhone')
    sofia_profile = models.ForeignKey('freeswitch.SofiaProfile')
    register_username = models.CharField(max_length=32, verbose_name="Username")
    register_password = models.CharField(max_length=32, verbose_name="Password")
    voicemail_password = models.CharField(max_length=32, blank=True)
    toll_allow = models.CharField(max_length=28, choices=(
        # TODO: this is kinda silly, present this in a better way
        ('local', 'Local'),
        ('domestic', 'Domestic'),
        ('international', 'International'),
        ('local,domestic', 'Local & Domestic'),
        ('local,international', 'Local & International'),
        ('domestic,international', 'Domestic & International'),
        ('local,domestic,international', 'Local, Domestic, International'),
    ), default="local,domestic,international")
    accountcode = models.IntegerField(default=1000)
    user_context = models.CharField(max_length=32, blank=True,
        help_text="Uses context from the profile if not set here.")
    effective_caller_id_name = models.CharField(max_length=32, blank=True,
        verbose_name="Effective name")
    effective_caller_id_number = models.CharField(max_length=32, blank=True,
        verbose_name="Effective number")
    outbound_caller_id_name = models.CharField(max_length=32,
        default="$${outbound_caller_name}", verbose_name="Outbound name")
    outbound_caller_id_number = models.CharField(max_length=32,
        default="$${outbound_caller_id}", verbose_name="Outbound number")
    callgroup = models.CharField(max_length=32, blank=True)

    class Meta:
        app_label = 'freeswitch'

    def __unicode__(self):
        return self.name

    @property
    def dial_string(self):
        return self.sofia_profile.get_extension_dial_string(self)
