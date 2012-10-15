from django.contrib import admin
from parseltone.django.apps.freeswitch import models


class ACLAdmin(admin.ModelAdmin):
    list_display = ('name', 'default')
    list_filter = ('default',)
    filter_horizontal = ('nodes',)


class ACLNodeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type', 'domain', 'cidr', 'host', 'mask')
    list_filter = ('type',)
    fieldsets = (
        (None, {
            'fields': ('type', 'domain', 'cidr', ('host', 'mask')),
        }),
    )


class IVRMenuAdmin(admin.ModelAdmin):
    filter_horizontal = ('actions',)


class SofiaPhoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'mac_address', 'last_config_date')


class SofiaExtensionAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'dial_string')
    list_display_links = ('name',)
    fieldsets = (
        (None, {
            'fields': (
                ('phone', 'name'),
            ),
        }),
        ('Registration', {
            'fields': (
                'sofia_profile',
                ('register_username', 'register_password'),
            ),
        }),
        ('Calling Details', {
            'classes': ('collapse',),
            'fields': (
                'user_context',
                'toll_allow',
                'callgroup',
            ),
        }),
        ('Caller ID', {
            'classes': ('collapse',),
            'fields': (
                ('effective_caller_id_name', 'effective_caller_id_number'),
                ('outbound_caller_id_name', 'outbound_caller_id_number'),
            ),
        }),
        ('Voicemail', {
            'classes': ('collapse',),
            'fields': (
                ('accountcode', 'voicemail_password'),
            ),
        }),
    )


class SofiaGlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('freeswitch_server', 'log_level', 'auto_restart',
        'debug_presence')


class SofiaProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'domain', 'context'), 'slug',
                'freeswitch_server',
                'hold_music',
            ),
        }),
        ('Endpoint Registration', {
            'classes': ('collapse',),
            'fields': (
                'user_agent_string',
                ('apply_register_acl', 'accept_blind_reg'),
                'challenge_realm',
                ('force_register_domain', 'force_register_db_domain',
                    'inbound_reg_force_matching_username'),
                ('manage_presence', 'presence_hosts'),
            ),
        }),
        ('Inbound Calls', {
            'classes': ('collapse',),
            'fields': (
                'apply_inbound_acl',
                ('inbound_codec_prefs', 'inbound_codec_negotiation'),
            ),
        }),
        ('Outbound Calls', {
            'classes': ('collapse',),
            'fields': (
                ('auth_calls', 'auth_all_packets', 'accept_blind_auth',
                    'log_auth_failures'),
                'outbound_codec_prefs',
            ),
        }),
        ('Recording', {
            'fields': (
                ('record_path', 'record_template'),
            ),
        }),
        ('DTMF Handling', {
            'classes': ('collapse',),
            'fields': (
                'liberal_dtmf',
                ('dtmf_type', 'pass_rfc2833', 'dtmf_duration'),
            ),
        }),
        ('Networking', {
            'classes': ('collapse',),
            'fields': (
                'local_network_acl',
                ('aggressive_nat_detection', 'apply_nat_acl'),
            ),
        }),
        ('SIP & RTP', {
            'fields': (
                ('sip_ip', 'sip_port', 'ext_sip_ip'),
                ('rtp_ip', 'ext_rtp_ip'),
                ('rtp_timeout_sec', 'rtp_hold_timeout_sec', 'rtp_timer_name'),
            ),
        }),
        ('TLS', {
            'classes': ('collapse',),
            'fields': (
                ('tls', 'tls_version'),
                ('tls_sip_port', 'tls_bind_params', 'tls_cert_dir'),
            ),
        }),
        ('Watchdog', {
            'description': "Sometimes, in extremely rare edge cases, the "
                "Sofia SIP stack may stop responding. These options allow "
                "you to enable and control a watchdog on the Sofia SIP stack "
                "so that if it stops responding for the specified number of "
                "milliseconds, it will cause FreeSWITCH to crash immediately. "
                "This is useful if you run in an HA environment and need to "
                "ensure automated recovery from such a condition. Note that "
                "if your server is idle a lot, the watchdog may fire due to "
                "not receiving any SIP messages. Thus, if you expect your "
                "system to be idle, you should leave the watchdog disabled. "
                "It can be toggled on and off through the FreeSWITCH CLI "
                "either on an individual profile basis or globally for all "
                "profiles. So, if you run in an HA environment with a master "
                "and slave, you should use the CLI to make sure the watchdog "
                "is only enabled on the master. If such crash occurs, "
                "FreeSWITCH will dump core if allowed. The stacktrace will "
                "include function watchdog_triggered_abort().",
            'classes': ('collapse',),
            'fields': (
                ('watchdog_enabled', 'watchdog_step_timeout',
                'watchdog_event_timeout'),
            ),
        }),
        ('Debugging', {
            'classes': ('collapse',),
            'fields': (
                ('debug', 'sip_trace'),
            ),
        }),
    )


class EventSocketAdmin(admin.ModelAdmin):
    list_display = ('freeswitch_server', 'listen_ip', 'listen_port')
