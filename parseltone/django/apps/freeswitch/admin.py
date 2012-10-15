from django.contrib import admin
from parseltone.django.apps.freeswitch import admin_models, models

admin.site.register(models.ACL, admin_models.ACLAdmin)
admin.site.register(models.ACLNode, admin_models.ACLNodeAdmin)
admin.site.register(models.FreeswitchServer)
admin.site.register(models.SofiaGlobalSettings, admin_models.SofiaGlobalSettingsAdmin)
admin.site.register(models.SofiaProfile, admin_models.SofiaProfileAdmin)
admin.site.register(models.SofiaGateway)
admin.site.register(models.SofiaDomain)
admin.site.register(models.SofiaPhone, admin_models.SofiaPhoneAdmin)
admin.site.register(models.SofiaExtension, admin_models.SofiaExtensionAdmin)
admin.site.register(models.IVRMenu, admin_models.IVRMenuAdmin)
admin.site.register(models.IVRMenuAction)
admin.site.register(models.EventSocket, admin_models.EventSocketAdmin)

