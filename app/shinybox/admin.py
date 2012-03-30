from django.contrib import admin
from models import *

class GenericAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(ShinyBox, GenericAdmin)
admin.site.register(Uploader, GenericAdmin)
admin.site.register(Password, GenericAdmin)
admin.site.register(File, GenericAdmin)
