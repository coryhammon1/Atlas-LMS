from django.contrib import admin

from schoolmanager.bulletins.models import *

class BulletinInline(admin.TabularInline):
	model = Bulletin

class BulletinCommentInline(admin.TabularInline):
	model = BulletinComment

class BulletinBoardAdmin(admin.ModelAdmin):
    inlines = [BulletinInline,]
admin.site.register(BulletinBoard, BulletinBoardAdmin)

class BulletinAdmin(admin.ModelAdmin):
    inlines = [BulletinCommentInline,]
admin.site.register(Bulletin, BulletinAdmin)