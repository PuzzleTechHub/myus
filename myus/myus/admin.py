from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Hunt, Puzzle, GuessResponse, Team, Guess, ExtraGuessGrant


class GuessResponseInlineAdmin(admin.TabularInline):
    model = GuessResponse


class PuzzleAdmin(admin.ModelAdmin):
    inlines = [GuessResponseInlineAdmin]


admin.site.register(User, UserAdmin)
admin.site.register(Hunt)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(GuessResponse)
admin.site.register(Team)
admin.site.register(Guess)
admin.site.register(ExtraGuessGrant)
