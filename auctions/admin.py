from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category

# This will show date in the admin panel
class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)
