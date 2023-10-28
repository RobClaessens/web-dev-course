from django.contrib import admin
from .models import *


# Register models
admin.site.register(User)
admin.site.register(Portfolio)
admin.site.register(Stock)
admin.site.register(StockWatch)
admin.site.register(StockTransaction)
admin.site.register(FiatTransaction)
admin.site.register(StockDividend)
admin.site.register(FiatDividend)
