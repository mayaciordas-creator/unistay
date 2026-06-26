# UniStay — Sistem Digital de Cazare în Cămin Studențesc

**Autor:** Ciordaș Maya-Natalia
**Universitatea:** Universitatea Babeș-Bolyai, Cluj-Napoca
**Facultatea:** Științe Economice și Gestiunea Afacerilor (FSEGA)
**Specializarea:** Informatică Economică
**Coordonator:** Lect. univ. dr. Cristina Osman
**An:** 2026

## Descrierea Proiectului
UniStay este o platformă web dezvoltată în Python/Django care digitalizează integral procesul de cazare studențească. Sistemul rezolvă problemele birocratice tradiționale prin implementarea unui flux complet automatizat: de la autentificarea bazată pe roluri (RBAC), filtrarea și rezervarea camerelor, până la procesarea plăților online securizate prin Stripe și generarea codurilor QR pentru check-in instantaneu.

## Tehnologii Utilizate
* **Backend:** Python, Django Framework (Arhitectura MVT)
* **Frontend:** HTML5, CSS3, Bootstrap 5
* **Bază de Date:** SQLite (configurație de dezvoltare)
* **Procesare Plăți:** Stripe API
* **Altele:** Generare coduri QR (`qrcode`), Identificatori unici (`uuid`)

## Cerințe de Sistem
* Python 3.10 sau mai nou
* Manager de pachete `pip`

## Instrucțiuni de Instalare și Rulare

1. **Crearea unui mediu virtual (opțional, dar recomandat):**
   ```bash
   python -m venv venv
   # Activare pe Windows:
   venv\Scripts\activate
   # Activare pe Linux/Mac:
   source venv/bin/activate
   ```

2. **Instalarea dependențelor:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Aplicarea migrațiilor bazei de date:**
   ```bash
   python manage.py migrate
   ```

4. **Crearea unui cont de administrator (superuser):**
   ```bash
   python manage.py createsuperuser
   ```
   *(Atenție: După creare, va trebui asociat un `Profil` de administrator din panoul `/admin`)*

5. **Pornirea serverului de dezvoltare:**
   ```bash
   python manage.py runserver
   ```
   Aplicația va fi disponibilă la adresa `http://127.0.0.1:8000/`.

## Structura Proiectului
* `camin/` - Setările principale ale proiectului Django și rutarea globală.
* `cazare/` - Aplicația centrală care conține logica de business (modele, vizualizări, formulare).
* `templates/` - Șabloanele HTML structurate ierarhic.
* `static/` - Fișierele CSS pentru stilizare.
* `media/` - Director pentru stocarea fișierelor generate de utilizatori (coduri QR, documente).

## Licență
Acest proiect a fost dezvoltat exclusiv în scop academic, ca lucrare de licență.
