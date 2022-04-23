from django.contrib import admin
from .models import User, Category, Listing, Bid, Comment, Watching


# Register your models here.
# class FlightAdmin(admin.ModelAdmin):
# 	list_display = ("id", "origin", "destination", "duration")
#
#
# class PassengerAdmin(admin.ModelAdmin):
# 	filter_horizontal = ("flights",)


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watching)
