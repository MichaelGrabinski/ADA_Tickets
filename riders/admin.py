from django.contrib import admin
#@admin.register(ADARider)
class ADARiderAdmin(admin.ModelAdmin):
    list_display = ('last_name','first_name','ada_id','inactive','zip_code')
    search_fields = ('first_name','last_name','ada_id')
#admin.site.register(ADATicketPurchase)
#admin.site.register(RiderNote)
