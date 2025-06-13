from django.apps import AppConfig

class appConfig(AppConfig):  # use your actual app name here
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        import app.signals  
