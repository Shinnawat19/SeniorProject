from django.contrib import admin
from trading.models import BotDetail , BotAction, BotPortfolio

# Register your models here.


class BotDetailAdmin(admin.ModelAdmin):
    list_display = [ bot.name for bot in BotDetail._meta.fields ]
    
admin.site.register(BotDetail, BotDetailAdmin)

class BotActionAdmin(admin.ModelAdmin):
    list_display = [ bot.name for bot in BotAction._meta.fields ]

admin.site.register(BotAction, BotActionAdmin)

class BotPortfolioAdmin(admin.ModelAdmin):
    list_display = [ bot.name for bot in BotPortfolio._meta.fields ]

admin.site.register(BotPortfolio, BotPortfolioAdmin)