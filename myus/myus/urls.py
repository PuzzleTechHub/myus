from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('change-password', PasswordChangeView.as_view(template_name='change-password.html')),
    path('change-password/done', PasswordChangeDoneView.as_view(template_name='change-password-done.html'), name='password_change_done'),
    path('register', views.register, name='register'),

    path('new', views.new_hunt, name='new_hunt'),
    path('hunt/<int:id>', views.view_hunt, name='view_hunt'),
    path('hunt/<int:id>/team', views.my_team, name='my_team'),
    path('hunt/<int:id>/new', views.new_puzzle, name='new_puzzle'),
    path('hunt/<int:id>/leaderboard', views.leaderboard, name='leaderboard'),
    path('hunt/<int:hunt_id>/puzzle/<int:puzzle_id>', views.view_puzzle, name='view_puzzle'),
    path('hunt/<int:hunt_id>/puzzle/<int:puzzle_id>/edit', views.edit_puzzle, name='edit_puzzle'),
    path('hunt/<int:hunt_id>/puzzle/<int:puzzle_id>/log', views.view_puzzle_log, name='view_puzzle_log'),

    path('preview_markdown', views.preview_markdown, name='preview_markdown'),
]
