from django.contrib import admin
from .models import BotUser, RoadTranslation, SmmPost, RidePost, TelegramGroup, TelegramBot, Road
# Register your models here.


class RidePostAdmin(admin.ModelAdmin):
    list_display = ('id', 'ordered_by_user', 'accepted_by_user',
                    'is_active', 'short_description')
    list_filter = ('is_active', 'ordered_by', 'accepted_by')
    search_fields = ('description', 'ordered_by__user_id',
                     'accepted_by__user_id')
    list_select_related = ('ordered_by', 'accepted_by')

    def ordered_by_user(self, obj):
        return obj.ordered_by.user_id
    ordered_by_user.short_description = 'Ordered By'

    def accepted_by_user(self, obj):
        if obj.accepted_by:
            return obj.accepted_by.user_id
        return 'Not yet accepted'
    accepted_by_user.short_description = 'Accepted By'

    def short_description(self, obj):
        return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description
    short_description.short_description = 'Description'


class RoadTranslationInline(admin.TabularInline):
    model = RoadTranslation
    extra = 1


@admin.register(Road)
class RoadAdmin(admin.ModelAdmin):
    inlines = (RoadTranslationInline,)


admin.site.register(RoadTranslation)

admin.site.register(RidePost, RidePostAdmin)
admin.site.register(TelegramBot)
admin.site.register(BotUser)
admin.site.register(SmmPost)
admin.site.register(TelegramGroup)
