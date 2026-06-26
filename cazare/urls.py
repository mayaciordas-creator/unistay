"""
Configurarea URL-urilor pentru aplicația de cazare.

Fiecare URL este asociat cu o funcție view care procesează cererea.
Folosim funcția path() pentru a defini rutele.
"""

from django.urls import path
from . import views

urlpatterns = [
    # ---- Camere ----
    path('camere/', views.room_list, name='room_list'),
    path('camere/<int:pk>/', views.room_detail, name='room_detail'),

    # ---- Rezervări ----
    path('rezervare/<int:camera_id>/', views.reservation_create, name='reservation_create'),
    path('rezervare/anulare/<int:rezervare_id>/', views.reservation_cancel, name='reservation_cancel'),

    # ---- Plăți ----
    path('plata/<int:rezervare_id>/', views.payment_view, name='payment'),
    path('plata/proceseaza/<int:rezervare_id>/', views.process_payment, name='process_payment'),
    path('plata/succes/<int:rezervare_id>/', views.payment_success, name='payment_success'),
    path('plata/anulata/<int:rezervare_id>/', views.payment_cancelled, name='payment_cancelled'),
    path('plata/repeta/<int:rezervare_id>/', views.repeat_payment, name='repeat_payment'),

    # ---- Check-in ----
    path('checkin/', views.checkin_view, name='checkin'),
    path('checkin/proceseaza/', views.checkin_process, name='checkin_process'),

    # ---- Dashboard Student ----
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    # ---- Dashboard Admin ----
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/camere/', views.manage_rooms, name='manage_rooms'),
    path('admin-panel/camere/adauga/', views.add_room, name='add_room'),
    path('admin-panel/camere/editeaza/<int:pk>/', views.edit_room, name='edit_room'),
    path('admin-panel/camere/sterge/<int:pk>/', views.delete_room, name='delete_room'),
    path('admin-panel/rezervari/', views.manage_reservations, name='manage_reservations'),
    path('admin-panel/rezervari/update-status/<int:pk>/', views.update_reservation_status, name='update_reservation_status'),
    # ---- Admin Studenți ----
    path('admin-panel/studenti/', views.manage_students, name='manage_students'),
    path('admin-panel/studenti/update-status/<int:pk>/', views.update_student_status, name='update_student_status'),

    # ---- Activare cont prin e-mail ----
    path('activeaza/<uidb64>/<token>/', views.activate_account, name='activate_account'),
]
