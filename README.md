# AI-Based Driver Monitoring System

This repository began as a real-time driver safety monitoring system and has been extended into a practical taxi fleet safety management prototype.

## Project purpose

The system monitors drivers using a webcam and computer vision to detect drowsiness, yawning, distraction, and phone use. It logs risky events, plays audio alerts, and provides a Django dashboard that lets a fleet owner manage drivers, vehicles, assignments, and safety records.

## Core features

- Real-time drowsiness detection using MediaPipe landmark analysis and EAR
- Yawning detection using MAR logic
- Distraction detection with head pose thresholds
- YOLO-based phone detection
- Warning sounds and spoken alerts
- Safety scoring and event logging
- Django-based fleet owner dashboard for drivers, vehicles, and safety events
- Secure Django authentication for protected access

## Directory structure

```text
driver_safety_system/
├── README.md
├── requirements.txt
├── alerts.py
├── config.py
├── create_voice_alerts.py
├── event_logger.py
├── main.py
├── phone_detection.py
├── safety_score.py
├── events.csv
├── assets/
├── driversafetyenv/
├── face_landmarker.task
├── hand_landmarker.task
├── yolo11n.pt
├── fleet_management/
│   ├── manage.py
│   ├── .env.example
│   ├── fleet_management/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── tests.py
│   ├── dashboard/
│   ├── drivers/
│   ├── vehicles/
│   ├── safety_events/
│   ├── templates/
│   └── static/
├── tests/
└── .gitignore
```

## Setup

### 1. Activate the environment

```powershell
cd "C:\Users\JA TEJA REDDY\Desktop\MAIN\driver_safety_system"
.\driversafetyenv\Scripts\Activate.ps1
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare the fleet dashboard

Run migrations and create a dashboard login:

```powershell
cd fleet_management
python manage.py migrate
python manage.py createsuperuser
```

Fleet-owner pages require a Django account with **Staff status** enabled. A user
linked to a driver profile is treated as a driver, not an owner, even if staff
status is enabled. `createsuperuser` creates a staff account. Local development
defaults to `DEBUG=True`, a development-only secret fallback, and localhost
hosts; do not use those defaults for a public deployment.

Settings can be provided through process environment variables (the project
does not automatically load `.env.example`):

- `DJANGO_DEBUG`: `True` for local development; set `False` in production.
- `DJANGO_SECRET_KEY`: a private, randomly generated secret. Required when
  `DJANGO_DEBUG=False`; do not commit it.
- `DJANGO_ALLOWED_HOSTS`: comma-separated allowed hostnames; required in
  production, for example `fleet.example.com`.
- `DJANGO_SECURE_SSL_REDIRECT`: defaults to enabled outside debug mode. Set it
  according to the HTTPS/reverse-proxy setup.
- `DJANGO_SESSION_COOKIE_SECURE` and `DJANGO_CSRF_COOKIE_SECURE`: default to
  enabled outside debug mode.
- `DJANGO_SECURE_HSTS_SECONDS`: defaults to `0`; configure HSTS only after
  verifying HTTPS works for the deployment.
- `DJANGO_CACHE_BACKEND` and `DJANGO_CACHE_LOCATION`: default to a local-memory
  cache for development. Configure a shared Django-supported cache backend for
  multi-worker deployments so booking rate limits are shared between workers.
- `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`: optional Google
  OAuth web-client credentials. Configure both as environment variables to
  enable Google account registration and sign-in.
- `GOOGLE_MAPS_ROUTES_API_KEY`: optional server-side Google Routes API key.
  Enable the Routes API for the Google Cloud project and configure this key in
  the environment (do not commit it) to calculate live driving-distance fares
  for customer bookings. The customer fare is calculated at INR 20 per
  kilometer, rounded to two decimals. If the key is missing or the route
  service fails, the booking is not accepted with an invented fare.

### 4. Run the integrated fleet dashboard

From the fleet-management directory:

```powershell
cd fleet_management
python manage.py runserver
```

Open `http://127.0.0.1:8000/` (the dashboard, not `/admin/`) and sign in.
Manage drivers, vehicles, assignments, and safety events from the dashboard
navigation and action buttons. Select an active driver and vehicle in the **Live driver monitoring**
section and choose **Start monitor**. The dashboard launches the CV application
on the Django host, and detected events are recorded against the selected
driver and vehicle. Use **Stop monitoring** or press `Q` in the camera window
to stop it.

Fleet owners sign in at `/accounts/login/` using their registered email and
password. First-time owners may sign up at `/accounts/signup/`; owner access is
enabled only after email verification. Drivers sign in at `/drivers/login/`
using their Driver ID and password. To self-sign up, drivers must use the exact
name, Driver ID, and email already registered on an active profile by the fleet
owner. The new driver account is linked only after email verification. Booking
customers sign in at `/customers/login/` and create an account from
`/accounts/signup/`; customer access is activated only after email verification.
Customers can book a trip and see only their own booking history. Existing
owner-created password setup and reset links continue to work. Driver accounts
can view only their own profile and safety-event history.

Google signup/sign-in is shown when both `GOOGLE_OAUTH_CLIENT_ID` and
`GOOGLE_OAUTH_CLIENT_SECRET` are configured. Create a Google OAuth **Web
application** client and add the exact callback URI
`http://127.0.0.1:8000/accounts/google/login/callback/` (use the corresponding
HTTPS site URL in deployment). Set the credentials in the environment before
starting Django; do not put real credentials in `.env.example` or commit them.
Google owner and customer signup require a verified Google email. Google driver
signup also requires the driver ID and a verified Google email matching the
existing active driver profile. Without credentials, Google buttons stay hidden and
password signup/login continues to work.

Run the security and regression checks from the repository root with:

```powershell
driversafetyenv\Scripts\python.exe fleet_management\manage.py check
driversafetyenv\Scripts\python.exe fleet_management\manage.py test fleet_management.tests dashboard.tests dashboard.test_owner_dashboard safety_events.tests safety_events.test_csv_import vehicles.test_trips vehicles.test_locations drivers.test_portal_metrics
```

For local development, emails use Django's console backend: links are printed
in the terminal running `manage.py`, and the dashboard also displays a link to
copy. To deliver emails, configure SMTP environment variables before starting
Django, for example in PowerShell:

```powershell
$env:EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST = "smtp.example.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "true"
$env:EMAIL_HOST_USER = "your-smtp-user"
$env:EMAIL_HOST_PASSWORD = "your-smtp-password"
$env:DEFAULT_FROM_EMAIL = "Fleet Safety <noreply@example.com>"
```

The computer running Django must have access to the webcam and a graphical
desktop for the OpenCV camera window. The monitor's output is written to
`fleet_management/cv_monitor.log`.

To start the CV application without the dashboard, you can still run it
directly from the project root:

```powershell
python main.py
```

Events are appended to `events.csv` and saved to the dashboard database. When
started from the dashboard, each event is associated with the selected driver
and vehicle.

## Safety score logic

The system starts at 100 and subtracts based on event severity:

- Drowsiness: -15
- Yawning: -5
- Distraction: -10
- Phone usage: -15

Risk bands:

- 80–100: SAFE
- 60–79: MODERATE
- 40–59: WARNING
- Below 40: HIGH RISK
<!--  -->
## Fleet features included

- Add and edit drivers
- Register drivers from the dashboard with a profile photo, contact details, and license information
- View driver profile cards and uploaded photos from the dashboard
- Search drivers by name or ID
- Add, edit, and delete driver profiles from the dashboard
- Manage vehicles and registrations
- Add, edit, and delete vehicles from the dashboard
- Create, edit, end, and delete vehicle assignments
- Safety events are recorded automatically by CV monitoring; owners can correct event details and review status without deleting event records
- Owner dashboard with totals and recent incidents
- SQLite-backed prototype suitable for local development

## Testing

```bash
cd fleet_management
python manage.py test safety_events.tests
```

## Notes and limitations

- The YOLO phone detection is a useful indicator but is not a guaranteed proof of phone use in every case.
- This is a prototype built for local testing and demonstration.
- Real-world deployment would need stronger privacy controls, retention rules, and production-grade monitoring infrastructure.

## Fleet dashboard additions

The fleet prototype in this repository uses the existing Django application and SQLite database rather than adding a second Streamlit application. This preserves the current owner/driver login boundary and avoids duplicating fleet records.

- Owner overview: registered and active taxi counts, filtered event totals, seven-day event counts, event categories, taxi summaries, and an unreviewed-alert queue. Trips and the fleet score are shown from stored data; no validated fleet score is currently configured.
- Driver Safety Centre: live database totals, daily/weekly counts, category distribution, unresolved/high-priority queue, recent alerts, and a 30-day trend. Owners can filter by date, driver, taxi, trip, category, severity, status, and search text.
- Safety event management: searchable, paginated records, filtered CSV export, event context, and owner-only driver safety profiles. Repeated-event summaries use a visible threshold of at least three events for the same driver/category in the selected date range. They are prompts for review, not safety or employment labels.
- Configure the repeated-event threshold with the positive-integer `SAFETY_REPEATED_EVENT_THRESHOLD` environment variable (default `3`); changes take effect when Django restarts.
- Review workflow: New → Under Review → Acknowledged → Resolved, with validated forward transitions, optional notes, reviewer identity, and timestamped audit history. Resolved alerts are retained. Historical `reviewed` and `dismissed` values remain visible as legacy states.
- Customer bookings: verified customer accounts submit CSRF-protected requests at `/vehicles/book/`. The pickup and destination are sent server-side to Google Routes API for driving distance; the fare is shown live at INR 20/km and recalculated server-side when the booking is submitted. The Google API key is never sent to the browser. The form validates a future pickup time, phone number, and passenger count, uses a honeypot, and limits each remote address to five submissions per hour using Django's configured cache. Customers can review only their own bookings at `/vehicles/my-bookings/`. Owners can filter, inspect, assign an eligible active driver and taxi, confirm, or cancel requests. Confirmation creates one linked planned trip with the quoted route distance and fare; the assigned driver sees the trip in their portal, starts it there, and may share GPS during the active trip for owner monitoring. Cancellation preserves both the customer request and linked trip.
- Trip lifecycle: owners schedule trips with an active driver and taxi. Assigned drivers start and complete their own trips from the driver portal. The server records actual start/end times and rejects invalid state transitions. Owners can cancel planned or in-progress trips; cancellation timestamps are retained. The database prevents two in-progress trips per driver/taxi and duplicate planned assignments for the same driver/taxi and pickup time. A driver's license expiry is checked when eligible assignment is made.
- Trips and reports: trip IDs, scheduled pickup, optional distance/fare and route, lifecycle state, and linked safety events. Values are not inferred from GPS. Reports can be grouped daily, weekly, or monthly and exported as CSV.
- Taxi finances: fleet owners can record and correct vehicle expenses for fuel, maintenance, tolls, parking, driver payments, and other operating costs; expenses can optionally reference a trip and receipt. The finance report groups expenses and existing trip fares by taxi and filters by date or vehicle. Revenue uses the existing fare on completed trips, dated by trip completion; cancelled and incomplete trips do not count, and a linked booking is not counted separately. The current schema has no billed/collected/payment state, so recorded fares are not proof that money was received. Net operating profit is recorded completed-trip fares less recorded operating expenses; it is not accounting or tax-adjusted profit. No historical financial records are fabricated. Currency defaults to INR and can be changed with `FINANCIAL_CURRENCY_CODE`.
- GPS locations: a signed-in driver can share phone location from their portal only during an active trip assigned to them and an active taxi. The browser sends a CSRF-protected session request to `POST /api/gps/locations/`; the server derives the driver from the authenticated account and checks the trip/vehicle assignment. No bearer secret is embedded in the page. Updates are throttled, validated, and stored as timestamped latitude/longitude points. Drivers must explicitly press **Start Sharing**; they can stop at any time. Fleet owners can view active-trip status, driver/taxi identifiers, the latest coordinates, and whether the signal is fresh, stale, or unavailable; dashboards refresh every 30 seconds.
- Phone location sharing requires browser location permission and HTTPS in deployed environments (localhost is generally allowed for development). It runs only while the driver portal is open and visible; browser or operating-system suspension, locking, or closing the page can stop updates. The page does not claim to track in the background. The browser update interval defaults to 30 seconds and the server allows at most one update every 20 seconds; configure `GPS_LOCATION_SHARING_INTERVAL_SECONDS` and `GPS_LOCATION_MIN_INTERVAL_SECONDS` in the environment (the browser interval must be at least the server minimum). Dashboard history is limited to 30 days. The existing `purge_trip_locations` command deletes older records only when an operator runs it; no automatic cleanup schedule is configured.
- Map links open OpenStreetMap only when clicked; the coordinate is then sent to that external map provider. The dashboard itself does not fetch map tiles or send coordinates to a third party.
- Camera events retain the monitor's existing driver/taxi association. The existing logger continues to append the original four-column CSV and saves the event directly through the Django bridge; deterministic event IDs also make later CSV imports idempotent for these rows. There is no public event-submission endpoint or separate ingestion service to run. Because the camera interface has no trip selection, link a recorded alert to a trip from its owner edit page or import a CSV row with a matching Trip ID.
- Driver portal: the authenticated driver's own events and trips, event counts, seven-day trend, and safety reminders. Its experimental lifetime indicator uses `100 - (15 x drowsiness + 5 x yawning + 10 x distraction + 15 x phone-use events)`, bounded at zero. It is not a validated crash-risk score and must not be used alone for employment or disciplinary decisions.
- Booking abuse protection uses the configured Django cache. The default local-memory cache is suitable only for local development; production deployments with multiple workers should configure a shared cache and network-level rate limiting.
- CSV import: legacy `Date,Time,Event,Duration (seconds)` files can be imported idempotently. Optional Driver ID, Taxi ID/Vehicle ID, Driver Name, and Trip ID fields are read where present. Driver names are not used to infer identity. Missing optional associations are left unlinked with explanatory event notes; malformed rows are reported and skipped. Import does not edit the source CSV.

### Windows CMD setup and operation

Run commands from a **Command Prompt** (`cmd.exe`) unless noted.

1. Back up the project before applying further code or database changes:

   ```cmd
   robocopy "C:\Users\JA TEJA REDDY\Desktop\MAIN\driver_safety_system" "C:\Users\JA TEJA REDDY\Desktop\MAIN\driver_safety_system_backup" /E /XD .git driversafetyenv /R:2 /W:2
   ```

   This copies project data, including `events.csv` and the SQLite database, but excludes Git internals and the virtual environment. Keep the backup private because it may contain driver records.

2. Activate the existing environment:

   ```cmd
   cd /d "C:\Users\JA TEJA REDDY\Desktop\MAIN\driver_safety_system"
   driversafetyenv\Scripts\activate.bat
   ```

3. Install project dependencies, including the Django Allauth Google OAuth integration:

   ```cmd
   python -m pip install -r requirements.txt
   ```

4. Apply the Django schema migrations:

   ```cmd
   python fleet_management\manage.py migrate
   ```

   To create a fleet-owner login if one does not exist:

   ```cmd
   python fleet_management\manage.py createsuperuser
   ```

5. To start the existing computer-vision monitor directly, use a terminal with the virtual environment active:

   ```cmd
   driversafetyenv\Scripts\python.exe main.py
   ```

   The monitor uses the existing `FLEET_DRIVER_ID` and `FLEET_VEHICLE_ID` settings from `config.py` (or environment variables with those names). Set them in that terminal before launch when using a non-default driver/taxi. When monitoring is started from the owner dashboard, it supplies the selected identifiers automatically. No separate event-ingestion process or public submission endpoint is used.

6. In a separate terminal, start the fleet web application:

   ```cmd
   cd /d "C:\Users\JA TEJA REDDY\Desktop\MAIN\driver_safety_system"
   driversafetyenv\Scripts\python.exe fleet_management\manage.py runserver 127.0.0.1:8000
   ```

7. Open the local owner dashboard at `http://127.0.0.1:8000/`. The driver sign-in page is `http://127.0.0.1:8000/drivers/login/`.

   Owners can register or sign in with email and password at `/accounts/signup/` and `/accounts/login/`. Drivers use `/drivers/login/`; first-time drivers choose **Create your account** and provide the name, Driver ID, and email already recorded by the owner. Email verification links are printed by Django's console email backend locally. Google signup/sign-in requires `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`, plus the Google callback URL listed above.

8. Register driver profiles first from **Drivers > Add driver** (`/drivers/add/`). Driver self-signup is matched to the saved driver ID, name, and email, and activates only after the email is confirmed. Existing owner-issued password setup links remain supported. This process does not register a face: no `face_registry.py` or face registry was present in the inspected project.

9. Register taxis at `/vehicles/add/`, record trips at `/vehicles/trips/add/`, review trips at `/vehicles/trips/`, and review reports at `/vehicles/trip-reports/`.

   To show phone GPS data, assign the driver and active taxi to a trip, then have the driver sign in on their phone, start that trip, open **My Driver Portal**, and press **Start Sharing**. The browser asks for permission at that point. On the owner dashboard, view **Active trip locations** or open **Locations**. A stale or unavailable signal is not presented as live. Deployed sites must use HTTPS. The browser API is session-authenticated, CSRF-protected, and has no shared GPS bearer token.

10. Open the Driver Safety Centre at `/events/centre/`; browse and export filtered events at `/events/`. Driver profiles are linked from event and repeated-event summaries. To import the root `events.csv` into SQLite after backing up the database, run:

    ```cmd
    driversafetyenv\Scripts\python.exe fleet_management\manage.py import_events_csv
    ```

    The import command reports invalid rows and skips duplicate event identifiers. It never writes to the original CSV. A separate importer process is not required: the current monitor logger writes to the Django database directly. Migrations `safety_events.0003`–`0005` add review history/statuses and allow duration and severity to remain explicitly unrecorded; they preserve existing event records and values.

11. Common troubleshooting:

    - `ModuleNotFoundError: django`: activate `driversafetyenv` and check `python -m pip show Django`.
    - Missing database tables: back up the project, then run `python fleet_management\manage.py migrate`.
    - Camera cannot open: close other applications using the webcam. Do not start `main.py` while also starting the dashboard's **Live driver monitoring** control; both launch the same camera application.
    - For a failed CSV import, check its column headers and the row numbers reported by the command. Correct the source only after making a separate backup.

12. Database backup and restore:

    ```cmd
    copy fleet_management\db.sqlite3 fleet_management\db.sqlite3.backup
    copy fleet_management\db.sqlite3.backup fleet_management\db.sqlite3
    ```

    Stop the Django server before restoring. Keep the backup outside the project if it contains personal information.

13. Run the Django checks and the test modules explicitly:

    ```cmd
    driversafetyenv\Scripts\python.exe fleet_management\manage.py check
    driversafetyenv\Scripts\python.exe fleet_management\manage.py test fleet_management.tests dashboard.tests dashboard.test_owner_dashboard safety_events.tests safety_events.test_csv_import vehicles.test_trips vehicles.test_locations drivers.test_portal_metrics
    ```

### Rollback and current worktree warning

The project already had uncommitted changes and the entire `fleet_management` directory was untracked before this implementation. Do not run `git clean`, `git checkout -- .`, or a blanket `git restore`; these can erase that pre-existing work. Review `git status --short` and `git diff` first. The safest rollback for this workspace is restoring the specific files from a project backup made before changes. For a clean Git rollback in a future checkout, commit or otherwise checkpoint the pre-existing work first, then revert only the commits made for the dashboard changes.

This is a local prototype. Before production, configure secrets, `DEBUG`, allowed hosts, HTTPS, role-specific authorization, audit logging, biometric consent/retention policies, and protected storage. Face matching is not implemented here, and face recognition must not be used as login authentication.
