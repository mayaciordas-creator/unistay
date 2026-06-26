"""

View-urile sunt funcții Python care primesc cereri HTTP (request)
și returnează răspunsuri HTTP (response) - de obicei pagini HTML.

Strcutura:
1. Pagini publice (home)
2. Autentificare (register, login, logout)
3. Camere (listare, detalii)
4. Rezervări (creare, vizualizare)
5. Plăți (Stripe Checkout)
6. QR Code (generare, afișare)
7. Check-in digital
8. Dashboard student
9. Dashboard admin (management camere, rezervări, studenți)
10. Plăți recurente
"""

import json
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

import stripe

from .models import Profil, Cladire, Camera, Rezervare, Plata
from .forms import InregistrareForm, CameraForm, RezervareForm, CheckinForm
from .decorators import admin_required, student_required


# ============================================================
# 1. PAGINI PUBLICE
# ============================================================

def home(request):
    """
    Pagina principală a aplicației.
    Afișează informații generale și statistici.
    """
    # Statistici pentru pagina principală
    total_camere = Camera.objects.count()
    camere_disponibile = Camera.objects.filter(locuri_disponibile__gt=0).count()
    total_cladiri = Cladire.objects.count()

    context = {
        'total_camere': total_camere,
        'camere_disponibile': camere_disponibile,
        'total_cladiri': total_cladiri,
    }
    return render(request, 'home.html', context)


# ============================================================
# 2. AUTENTIFICARE
# ============================================================

def register_view(request):
    """
    Pagina de înregistrare.
    Creează un cont nou cu profil de student sau admin.
    Contul este inactiv până la confirmarea adresei de e-mail.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = InregistrareForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            form.save_profile(user)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            activation_link = f"{site_url}/activeaza/{uid}/{token}/"

            send_mail(
                subject='UniStay — Confirmă adresa de e-mail',
                message=(
                    f'Bună, {user.first_name}!\n\n'
                    f'Îți mulțumim pentru înregistrarea în platforma UniStay.\n'
                    f'Apasă pe link-ul de mai jos pentru a-ți activa contul:\n\n'
                    f'{activation_link}\n\n'
                    f'Dacă nu ai creat un cont, ignoră acest mesaj.\n\n'
                    f'Echipa UniStay'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.info(
                request,
                f'Contul a fost creat! Verifică adresa {user.email} și apasă link-ul de activare.'
            )
            return redirect('login')
    else:
        form = InregistrareForm()

    return render(request, 'registration/register.html', {'form': form})


def activate_account(request, uidb64, token):
    """
    Activează contul utilizatorului pe baza token-ului primit pe e-mail.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(
            request,
            f'Bine ai venit, {user.first_name}! Contul tău a fost activat cu succes.'
        )
        return redirect('dashboard')
    else:
        messages.error(
            request,
            'Link-ul de activare este invalid sau a expirat. Încearcă să te înregistrezi din nou.'
        )
        return redirect('register')


@login_required
def dashboard_redirect(request):
    """
    Redirecționează utilizatorul către dashboard-ul corespunzător
    (admin sau student) pe baza rolului său.
    """
    if hasattr(request.user, 'profil') and request.user.profil.este_admin:
        return redirect('admin_dashboard')
    elif request.user.is_superuser:
        return redirect('admin_dashboard')
    else:
        return redirect('student_dashboard')


# ============================================================
# 3. CAMERE - Listare și detalii
# ============================================================

def room_list(request):
    """
    Afișează lista camerelor disponibile.
    Permite filtrarea după clădire, etaj și gen.
    """
    camere = Camera.objects.all()

    # Filtrare după clădire (dacă parametrul este trimis)
    cladire_id = request.GET.get('cladire')
    if cladire_id:
        camere = camere.filter(cladire_id=cladire_id)

    # Filtrare după etaj
    etaj = request.GET.get('etaj')
    if etaj:
        camere = camere.filter(etaj=etaj)

    # Filtrare după gen cameră
    gen_camera = request.GET.get('gen_camera')
    if gen_camera:
        camere = camere.filter(gen_camera=gen_camera)

    # Filtrare doar camere disponibile
    doar_disponibile = request.GET.get('disponibile')
    if doar_disponibile:
        camere = camere.filter(locuri_disponibile__gt=0)

    # Toate clădirile pentru dropdown-ul de filtare
    cladiri = Cladire.objects.all()

    context = {
        'camere': camere,
        'cladiri': cladiri,
        'cladire_selectata': cladire_id,
        'etaj_selectat': etaj,
        'gen_camera_selectat': gen_camera,
        'doar_disponibile': doar_disponibile,
    }
    return render(request, 'cazare/room_list.html', context)


def room_detail(request, pk):
    """
    Afișează detaliile unei camere specifice.
    pk = primary key (ID-ul camerei)
    """
    camera = get_object_or_404(Camera, pk=pk)
    context = {
        'camera': camera,
    }
    return render(request, 'cazare/room_detail.html', context)


# ============================================================
# 4. REZERVĂRI
# ============================================================

@login_required
@student_required
def reservation_create(request, camera_id):
    """
    Creează o rezervare nouă pentru o cameră.
    Doar studenții pot face rezervări.
    """
    camera = get_object_or_404(Camera, pk=camera_id)

    # Verifică dacă camera mai are locuri disponibile
    if not camera.este_disponibila:
        messages.error(request, 'Ne pare rău, această cameră nu mai are locuri disponibile.')
        return redirect('room_list')

    # Verifică dacă genul studentului se potrivește cu genul camerei
    if hasattr(request.user, 'profil') and camera.gen_camera != 'mixt':
        if request.user.profil.gen != camera.gen_camera:
            messages.error(
                request,
                f'Această cameră este destinată studenților de gen {camera.get_gen_camera_display()}. '
                f'Nu poți face o rezervare aici.'
            )
            return redirect('room_list')

    # Verifică dacă studentul este deja cazat
    if hasattr(request.user, 'profil') and request.user.profil.status_cazare == 'cazat':
        messages.warning(request, 'Ești deja cazat și nu mai poți face alte rezervări. Contactează administrația pentru a te decaza.')
        return redirect('student_dashboard')

    # Verifică dacă studentul are deja o rezervare activă
    rezervare_activa = Rezervare.objects.filter(
        student=request.user,
        status__in=['pending', 'confirmed', 'checked_in']
    ).first()

    if rezervare_activa:
        messages.warning(
            request,
            'Ai deja o rezervare activă. Finalizează sau anulează rezervarea existentă.'
        )
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = RezervareForm(request.POST, request.FILES)
        if form.is_valid():
            rezervare = form.save(commit=False)
            rezervare.student = request.user
            rezervare.camera = camera
            # Codul unic se generează automat în model.save()
            rezervare.save()

            # Scade un loc disponibil din cameră
            camera.locuri_disponibile -= 1
            camera.save()

            messages.success(request, 'Rezervarea a fost creată cu succes! Procedează la plată.')
            return redirect('payment', rezervare_id=rezervare.id)
    else:
        form = RezervareForm()

    context = {
        'form': form,
        'camera': camera,
    }
    return render(request, 'cazare/reservation_form.html', context)


@login_required
def reservation_cancel(request, rezervare_id):
    """
    Anulează o rezervare existentă.
    Eliberează locul din cameră.
    """
    rezervare = get_object_or_404(Rezervare, pk=rezervare_id, student=request.user)

    if rezervare.status in ['pending', 'confirmed']:
        rezervare.status = 'cancelled'
        rezervare.save()

        # Eliberează locul în cameră
        camera = rezervare.camera
        camera.locuri_disponibile += 1
        camera.save()

        messages.success(request, 'Rezervarea a fost anulată cu succes.')
    else:
        messages.error(request, 'Această rezervare nu poate fi anulată.')

    return redirect('student_dashboard')


# ============================================================
# 5. PLĂȚI (Stripe Checkout)
# ============================================================

@login_required
def payment_view(request, rezervare_id):
    """
    Pagina de plată pentru o rezervare.
    Creează o sesiune Stripe Checkout sau afișează plata simulată.
    """
    rezervare = get_object_or_404(Rezervare, pk=rezervare_id, student=request.user)

    # Verifică dacă plata a fost deja efectuată
    if hasattr(rezervare, 'plata') and rezervare.plata.status == 'completed':
        messages.info(request, 'Plata a fost deja efectuată.')
        return redirect('payment_success', rezervare_id=rezervare.id)

    # Calculează suma (preț lunar * număr luni)
    if rezervare.data_start and rezervare.data_sfarsit:
        luni = max(1, (rezervare.data_sfarsit - rezervare.data_start).days // 30)
        suma = float(rezervare.camera.pret_lunar) * luni
    else:
        suma = float(rezervare.camera.pret_lunar)

    # Încearcă integrarea Stripe reală
    stripe_session_id = None
    stripe_error = None
    use_stripe = not settings.STRIPE_SECRET_KEY.startswith('sk_test_simulare')

    if use_stripe:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'ron',
                        'product_data': {
                            'name': f'Cazare {rezervare.camera} - {luni if rezervare.data_start and rezervare.data_sfarsit else 1} luni',
                            'description': f'Rezervare #{rezervare.cod_unic}',
                        },
                        'unit_amount': int(suma * 100),  # Stripe folosește bani (centime)
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(f'/plata/succes/{rezervare.id}/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(f'/plata/anulata/{rezervare.id}/'),
                metadata={
                    'rezervare_id': rezervare.id,
                    'cod_unic': rezervare.cod_unic,
                },
            )
            stripe_session_id = checkout_session.id
        except Exception as e:
            stripe_error = str(e)
            use_stripe = False

    context = {
        'rezervare': rezervare,
        'suma': suma,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_session_id': stripe_session_id,
        'stripe_error': stripe_error,
        'use_stripe': use_stripe,
    }
    return render(request, 'cazare/payment.html', context)


@login_required
def process_payment(request, rezervare_id):
    """
    Procesează plata (Stripe sau simulare).
    """
    if request.method != 'POST':
        return redirect('payment', rezervare_id=rezervare_id)

    rezervare = get_object_or_404(Rezervare, pk=rezervare_id, student=request.user)

    # Calculează suma
    if rezervare.data_start and rezervare.data_sfarsit:
        luni = max(1, (rezervare.data_sfarsit - rezervare.data_start).days // 30)
        suma = float(rezervare.camera.pret_lunar) * luni
    else:
        suma = float(rezervare.camera.pret_lunar)

    # Verifică dacă este plată Stripe reală sau simulare
    use_stripe = not settings.STRIPE_SECRET_KEY.startswith('sk_test_simulare')

    if use_stripe:
        # Verifică sesiunea Stripe
        session_id = request.POST.get('stripe_session_id', '')
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            payment_id = session.payment_intent
        except Exception:
            payment_id = f"stripe_{uuid.uuid4().hex[:16]}"
    else:
        # Simulare Stripe
        payment_id = f"sim_{uuid.uuid4().hex[:16]}"

    # Creează sau actualizează înregistrarea plății
    plata, created = Plata.objects.get_or_create(
        rezervare=rezervare,
        defaults={
            'suma': suma,
            'stripe_payment_id': payment_id,
            'status': 'completed',
        }
    )

    if not created:
        plata.suma = suma
        plata.stripe_payment_id = payment_id
        plata.status = 'completed'
        plata.save()

    # Actualizează statusul rezervării la "confirmată"
    rezervare.status = 'confirmed'
    rezervare.save()

    # Generează codul QR
    genereaza_qr_code(rezervare)

    messages.success(request, 'Plata a fost procesată cu succes! Rezervarea ta este confirmată.')
    return redirect('payment_success', rezervare_id=rezervare.id)


@login_required
def payment_success(request, rezervare_id):
    """
    Pagina de succes după plată.
    Afișează confirmarea și codul QR.
    Dacă vine de la Stripe Checkout, verifică și finalizează plata.
    """
    rezervare = get_object_or_404(Rezervare, pk=rezervare_id, student=request.user)

    # Dacă vine de la Stripe Checkout cu session_id, finalizează plata
    session_id = request.GET.get('session_id')
    if session_id and not (hasattr(rezervare, 'plata') and rezervare.plata.status == 'completed'):
        # Calculează suma
        if rezervare.data_start and rezervare.data_sfarsit:
            luni = max(1, (rezervare.data_sfarsit - rezervare.data_start).days // 30)
            suma = float(rezervare.camera.pret_lunar) * luni
        else:
            suma = float(rezervare.camera.pret_lunar)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            payment_id = session.payment_intent or f"stripe_{uuid.uuid4().hex[:16]}"
        except Exception:
            payment_id = f"stripe_{uuid.uuid4().hex[:16]}"

        plata, created = Plata.objects.get_or_create(
            rezervare=rezervare,
            defaults={
                'suma': suma,
                'stripe_payment_id': payment_id,
                'status': 'completed',
            }
        )
        if not created and plata.status != 'completed':
            plata.stripe_payment_id = payment_id
            plata.status = 'completed'
            plata.save()

        if rezervare.status == 'pending':
            rezervare.status = 'confirmed'
            rezervare.save()
            genereaza_qr_code(rezervare)

    context = {
        'rezervare': rezervare,
    }
    return render(request, 'cazare/payment_success.html', context)


@login_required
def payment_cancelled(request, rezervare_id):
    """
    Pagina afișată când utilizatorul anulează plata Stripe.
    """
    rezervare = get_object_or_404(Rezervare, pk=rezervare_id, student=request.user)
    messages.warning(request, 'Plata a fost anulată. Poți încerca din nou.')
    return redirect('payment', rezervare_id=rezervare.id)


# ============================================================
# 6. GENERARE COD QR
# ============================================================

def genereaza_qr_code(rezervare):
    """
    Generează un cod QR unic pentru o rezervare.

    Codul QR conține un JSON cu:
    - ID-ul rezervării
    - numele studentului
    - codul unic al rezervării

    Imaginea este salvată în media/qr_codes/.
    """
    # Datele care vor fi codificate în QR
    qr_data = json.dumps({
        'reservation_id': rezervare.id,
        'student': rezervare.student.get_full_name() or rezervare.student.username,
        'cod_unic': rezervare.cod_unic,
        'camera': str(rezervare.camera),
    })

    # Creează obiectul QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Creează imaginea QR
    img = qr.make_image(fill_color="black", back_color="white")

    # Salvează imaginea într-un buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Salvează imaginea în modelul Rezervare
    filename = f"qr_{rezervare.cod_unic}.png"
    rezervare.qr_code.save(filename, File(buffer), save=True)

    return rezervare


# ============================================================
# 7. CHECK-IN DIGITAL
# ============================================================

def checkin_view(request):
    """
    Pagina de check-in digital.
    Permite introducerea codului unic pentru validare.
    """
    form = CheckinForm()
    return render(request, 'cazare/checkin.html', {'form': form})


def checkin_process(request):
    """
    Procesează cererea de check-in.
    Validează codul unic și marchează rezervarea ca 'check-in realizat'.
    """
    if request.method != 'POST':
        return redirect('checkin')

    form = CheckinForm(request.POST)
    if not form.is_valid():
        return render(request, 'cazare/checkin.html', {'form': form})

    cod_unic = form.cleaned_data['cod_unic'].strip().upper()

    # Caută rezervarea cu codul unic
    try:
        rezervare = Rezervare.objects.get(cod_unic=cod_unic)
    except Rezervare.DoesNotExist:
        messages.error(request, 'Codul introdus nu este valid. Verifică și încearcă din nou.')
        return render(request, 'cazare/checkin_result.html', {
            'success': False,
            'cod_unic': cod_unic,
        })

    # Verifică statusul rezervării
    if rezervare.status == 'checked_in':
        messages.warning(request, 'Check-in-ul a fost deja realizat pentru această rezervare.')
        return render(request, 'cazare/checkin_result.html', {
            'success': False,
            'rezervare': rezervare,
            'mesaj': 'Check-in-ul a fost deja realizat.',
        })

    if rezervare.status != 'confirmed':
        messages.error(request, 'Rezervarea nu este confirmată. Plata trebuie finalizată înainte de check-in.')
        return render(request, 'cazare/checkin_result.html', {
            'success': False,
            'rezervare': rezervare,
            'mesaj': 'Rezervarea nu este confirmată.',
        })

    # Marchează check-in-ul
    rezervare.status = 'checked_in'
    rezervare.save()

    # Sincronizare automată a statusului studentului
    if hasattr(rezervare.student, 'profil'):
        profil_student = rezervare.student.profil
        profil_student.status_cazare = 'cazat'
        profil_student.save()

    messages.success(request, 'Check-in realizat cu succes!')
    return render(request, 'cazare/checkin_result.html', {
        'success': True,
        'rezervare': rezervare,
    })


# ============================================================
# 8. DASHBOARD STUDENT
# ============================================================

@login_required
@student_required
def student_dashboard(request):
    """
    Panoul de control al studentului.
    Afișează rezervările, plățile și codurile QR ale studentului.
    """
    rezervari = Rezervare.objects.filter(student=request.user)

    context = {
        'rezervari': rezervari,
        'rezervare_activa': rezervari.filter(status__in=['pending', 'confirmed', 'checked_in']).first(),
    }
    return render(request, 'cazare/student_dashboard.html', context)


# ============================================================
# 9. DASHBOARD ADMIN
# ============================================================

@login_required
@admin_required
def admin_dashboard(request):
    """
    Panoul de control al administratorului.
    Afișează statistici și acces rapid la management.
    """
    context = {
        'total_camere': Camera.objects.count(),
        'camere_disponibile': Camera.objects.filter(locuri_disponibile__gt=0).count(),
        'total_rezervari': Rezervare.objects.count(),
        'rezervari_pending': Rezervare.objects.filter(status='pending').count(),
        'rezervari_confirmed': Rezervare.objects.filter(status='confirmed').count(),
        'rezervari_checkedin': Rezervare.objects.filter(status='checked_in').count(),
        'total_studenti': Profil.objects.filter(rol='student').count(),
        'total_cladiri': Cladire.objects.count(),
    }
    return render(request, 'cazare/admin_dashboard.html', context)


@login_required
@admin_required
def manage_rooms(request):
    """
    Pagina de management al camerelor (admin).
    Listează toate camerele cu opțiuni de editare.
    """
    camere = Camera.objects.all()
    return render(request, 'admin_panel/manage_rooms.html', {'camere': camere})


@login_required
@admin_required
def add_room(request):
    """
    Adaugă o cameră nouă (admin).
    """
    if request.method == 'POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Camera a fost adăugată cu succes!')
            return redirect('manage_rooms')
    else:
        form = CameraForm()

    return render(request, 'admin_panel/room_form.html', {
        'form': form,
        'titlu': 'Adaugă cameră nouă',
    })


@login_required
@admin_required
def edit_room(request, pk):
    """
    Editează o cameră existentă (admin).
    """
    camera = get_object_or_404(Camera, pk=pk)

    if request.method == 'POST':
        form = CameraForm(request.POST, instance=camera)
        if form.is_valid():
            form.save()
            messages.success(request, 'Camera a fost actualizată cu succes!')
            return redirect('manage_rooms')
    else:
        form = CameraForm(instance=camera)

    return render(request, 'admin_panel/room_form.html', {
        'form': form,
        'titlu': f'Editează camera {camera.numar}',
        'camera': camera,
    })


@login_required
@admin_required
def delete_room(request, pk):
    """
    Șterge o cameră (admin).
    """
    camera = get_object_or_404(Camera, pk=pk)

    if request.method == 'POST':
        camera.delete()
        messages.success(request, 'Camera a fost ștearsă cu succes!')
        return redirect('manage_rooms')

    return render(request, 'admin_panel/manage_rooms.html', {
        'camere': Camera.objects.all(),
        'camera_de_sters': camera,
    })


@login_required
@admin_required
def manage_reservations(request):
    """
    Pagina de management al rezervărilor (admin).
    Afișează toate rezervările cu posibilitate de filtrare.
    """
    rezervari = Rezervare.objects.all().select_related('student', 'camera')

    # Filtrare după status
    status = request.GET.get('status')
    if status:
        rezervari = rezervari.filter(status=status)

    context = {
        'rezervari': rezervari,
        'status_selectat': status,
    }
    return render(request, 'admin_panel/manage_reservations.html', context)


@login_required
@admin_required
def update_reservation_status(request, pk):
    """
    Actualizează statusul unei rezervări folosind un meniu dropdown din panoul admin.
    Gestionează automat eliberarea/ocuparea locurilor din cameră.
    """
    if request.method == 'POST':
        rezervare = get_object_or_404(Rezervare, pk=pk)
        nou_status = request.POST.get('status')
        status_valid = dict(Rezervare.STATUS_CHOICES)
        
        if nou_status in status_valid and nou_status != rezervare.status:
            vechiul_status = rezervare.status
            rezervare.status = nou_status
            rezervare.save()
            
            # Gestionare locuri disponibile
            statusuri_ocupate = ['pending', 'confirmed', 'checked_in']
            statusuri_libere = ['cancelled', 'rejected']
            camera = rezervare.camera
            
            if vechiul_status in statusuri_ocupate and nou_status in statusuri_libere:
                # Eliberează loc
                camera.locuri_disponibile += 1
                camera.save()
            elif vechiul_status in statusuri_libere and nou_status in statusuri_ocupate:
                # Ocupă loc (adminul forțează reactivarea)
                if camera.locuri_disponibile > 0:
                    camera.locuri_disponibile -= 1
                    camera.save()
                else:
                    messages.warning(request, 'Atenție: Statusul a fost modificat, dar camera nu mai are locuri fizice libere.')
            
            # Sincronizare automată a statusului studentului
            if hasattr(rezervare.student, 'profil'):
                profil_student = rezervare.student.profil
                if nou_status in ['confirmed', 'checked_in']:
                    profil_student.status_cazare = 'cazat'
                    profil_student.save()
                elif nou_status in ['cancelled', 'rejected']:
                    # Dacă rezervarea e anulată/respinsă, devine decazat
                    profil_student.status_cazare = 'decazat'
                    profil_student.save()
            
            messages.success(request, f'Statusul rezervării #{rezervare.cod_unic[:8]} a fost actualizat la "{status_valid[nou_status]}".')
            
    return redirect('manage_reservations')


@login_required
@admin_required
def manage_students(request):
    """
    Pagina de management al studenților (admin).
    Afișează toți studenții înregistrați.
    """
    studenti = Profil.objects.filter(rol='student').select_related('user')

    context = {
        'studenti': studenti,
    }
    return render(request, 'admin_panel/manage_students.html', context)


@login_required
@admin_required
def update_student_status(request, pk):
    """
    Actualizează statusul de cazare al unui student din admin panel.
    """
    if request.method == 'POST':
        profil = get_object_or_404(Profil, pk=pk)
        nou_status = request.POST.get('status_cazare')
        
        status_valid = dict(Profil.STATUS_CAZARE_CHOICES)
        if nou_status in status_valid:
            profil.status_cazare = nou_status
            profil.save()
            messages.success(request, f'Statusul pentru {profil.user.get_full_name() or profil.user.username} a fost actualizat la "{status_valid[nou_status]}".')
        else:
            messages.error(request, 'Status invalid.')
            
    return redirect('manage_students')


# ============================================================
# 10. PLĂȚI RECURENTE
# ============================================================

@login_required
@student_required
def repeat_payment(request, rezervare_id):
    """
    Permite studentului să repete o plată anterioară.
    Creează o nouă rezervare cu aceleași parametri ca cea veche
    și redirecționează către pagina de plată.
    """
    rezervare_veche = get_object_or_404(
        Rezervare, pk=rezervare_id, student=request.user
    )

    # Verifică dacă rezervarea veche a fost plătită
    if not hasattr(rezervare_veche, 'plata') or rezervare_veche.plata.status != 'completed':
        messages.error(request, 'Poți repeta doar plăți care au fost finalizate.')
        return redirect('student_dashboard')

    # Verifică dacă studentul are deja o rezervare activă
    rezervare_activa = Rezervare.objects.filter(
        student=request.user,
        status__in=['pending', 'confirmed']
    ).first()

    if rezervare_activa:
        messages.warning(
            request,
            'Ai deja o rezervare activă. Finalizează sau anulează-o mai întâi.'
        )
        return redirect('student_dashboard')

    # Verifică dacă camera mai are locuri
    camera = rezervare_veche.camera
    if not camera.este_disponibila:
        messages.error(request, 'Camera nu mai are locuri disponibile.')
        return redirect('room_list')

    # Calculează noile date (aceeași durată, dar din ziua curentă)
    from datetime import date, timedelta
    durata = (rezervare_veche.data_sfarsit - rezervare_veche.data_start).days
    data_start_noua = date.today()
    data_sfarsit_noua = data_start_noua + timedelta(days=durata)

    # Creează noua rezervare
    rezervare_noua = Rezervare(
        student=request.user,
        camera=camera,
        data_start=data_start_noua,
        data_sfarsit=data_sfarsit_noua,
    )
    rezervare_noua.save()

    # Scade un loc din cameră
    camera.locuri_disponibile -= 1
    camera.save()

    messages.success(
        request,
        f'Rezervare nouă creată pe baza rezervării #{rezervare_veche.cod_unic[:8]}. '
        f'Procedează la plată.'
    )
    return redirect('payment', rezervare_id=rezervare_noua.id)
