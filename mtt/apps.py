from django.contrib.admin.apps import AdminConfig

class MTTAdminConfig(AdminConfig):
    default_site = 'tournament.admin.MTTAdminSite'
