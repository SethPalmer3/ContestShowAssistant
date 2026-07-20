from django.contrib import admin
from .models import ServerState, ClientRole

@admin.register(ServerState)
class ServerStateAdmin(admin.ModelAdmin):
    list_display = ('mode', 'current_show', 'current_event')
    
    # These two functions enforce the Singleton pattern in the Admin UI
    def has_add_permission(self, request):
        # Prevent adding a new state if one already exists
        if self.model.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the core state
        return False

@admin.register(ClientRole)
class ClientRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)
