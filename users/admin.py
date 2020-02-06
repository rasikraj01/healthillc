from django.contrib import admin

from .models import Plan, Coupon, Profile

class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'duration')

class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_id', 'discount_percent', 'status')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','first_name', 'last_name',  'country' ,'contact_no')


admin.site.register(Plan, PlanAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Profile, ProfileAdmin)