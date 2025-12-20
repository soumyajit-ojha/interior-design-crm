from django.contrib import admin
from .models import VideoUser


class AdminVideoUser(admin.ModelAdmin):
    list_display = ["user_fk", "title_nn", "url", "description"]
    search_fields = ["user_fk__username", "user_fk__email", "title_nn", "url"]
    list_filter = ["user_fk__username", "user_fk__email", "title_nn", "url"]


admin.site.register(VideoUser, AdminVideoUser)
