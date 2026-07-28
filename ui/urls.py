from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.setup_dashboard, name='ui_setup'),
    path('score-keeper/', views.score_keeper, name='ui_score_keeper'),
    path('display/', views.score_display, name='ui_display'),
    path('admin-panel/', views.admin_panel, name='ui_admin'),
]
