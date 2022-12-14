from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import SupportSubmission, Profile, EventLog, Author, Project, ProjectAuthor, Commit, Diff, Issue, PullRequest, Comment, ProjectRole
 
# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')

@admin.register(SupportSubmission)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('user', 'datetime', 'supportType', 'feature', 'description')

@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_type', 'datetime')

@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'source_url', 'last_updated', 'fork_of')
 
@admin.register(ProjectAuthor)
class ProjecAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'author')
 
@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    list_display = ('id', 'hash', 'branch', 'datetime', 'message', 'project', 'author')
 
@admin.register(Diff)
class DiffAdmin(admin.ModelAdmin):
    list_display = ('id', 'commit', 'file_path', 'language', 'body')

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'author', 'created_at', 'project', 'url')

@admin.register(PullRequest)
class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'author', 'created_at', 'project', 'url')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'author', 'issue', 'pr')
