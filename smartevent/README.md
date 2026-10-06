# SmartEvent – Event Discovery & Ticket Booking (with Payments)

FastAPI + SQLAlchemy backend, React (Vite) frontend.

## Run it

**Backend** (Python 3.10+)
```bash
cd backend
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # set a real SECRET_KEY
uvicorn app.main:app --reload
```
API: http://localhost:8000 · Swagger docs: http://localhost:8000/docs  
Tables are created and 8 sample events seeded on first start (SQLite file `smartevent.db`).

**Frontend** (Node 18+)
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173 (set `VITE_API_URL` in `frontend/.env` if the API runs elsewhere).

## New: Module 7 – Payments

### Booking + payment flow
1. User picks quantity and clicks **Book and pay** → `POST /bookings` creates a `PENDING` booking and **reserves** the tickets (atomic stock update, no overselling). Total price is computed on the server.
2. Checkout page (`/payment/:bookingId`) shows the order summary and a hold countdown (default 15 min).
3. `POST /payments/pay` charges the booking:
   - **Success** → payment `SUCCESS`, booking `CONFIRMED`, unique ticket + QR generated, notifications created.
   - **Failure** → payment `FAILED` (reason stored); booking stays `PENDING`, user can retry.
4. Unpaid bookings expire after the hold; tickets return to stock automatically (background job + checked on every booking/payment call).
5. `POST /bookings/{id}/cancel` → confirmed bookings are **refunded** (payment `REFUNDED`), ticket `CANCELLED`, tickets returned to stock.

### Payments table
`id, booking_id, user_id, amount, currency, method (CARD/UPI/NETBANKING/WALLET), status (PENDING/SUCCESS/FAILED/REFUNDED), transaction_id, card_last4, failure_reason, refunded_at, created_at`

Other schema changes: `events.total_tickets / available_tickets` (needed for availability checks), `bookings.expires_at / reminder_sent`, `tickets.status (VALID/USED/CANCELLED)`.

### New endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/payments/pay` | Pay a pending booking |
| GET | `/payments` | Current user's payment history |
| GET | `/payments/{id}` | One payment (owner only) |
| POST | `/bookings/{id}/cancel` | Cancel (+ refund if paid) |
| POST | `/tickets/verify` | Entry-gate scan; marks ticket `USED` |

### Demo gateway test values
| Input | Result |
|---|---|
| Card `4111 1111 1111 1111` (any future expiry, any CVV) | Success |
| Card ending `0002` (e.g. `4000 0000 0000 0002`) | Declined |
| Card ending `9995` (e.g. `4000 0000 0000 9995`) | Insufficient funds |
| UPI id starting with `fail` | Declined |
| Bank "FailBank" | Declined |
| Anything else | Success |

### Security notes
- Card number and CVV go to the gateway only; **only the last 4 digits** are stored.
- Card numbers are Luhn-checked and expiry validated with Pydantic.
- Payment/booking/ticket access is owner-only; amounts are never taken from the client.
- Use HTTPS in production and set a strong `SECRET_KEY`.

### Using a real provider (Stripe / Razorpay)
`app/services/payment_gateway.py` defines the `PaymentGateway` protocol (`charge`, `refund`). Implement it with your provider's SDK, return it from `get_gateway()`, and set `PAYMENT_PROVIDER`. For real card handling, use the provider's hosted fields/checkout so raw card data never reaches your server (PCI scope), and confirm payments via webhooks.

## Event images
Banners are custom SVG illustrations in `backend/static/banners/` (served at `/static/banners/...`), referenced from `backend/app/seed.py`. To use your own photo, put it in that folder and set `banner_image="/static/banners/my-photo.jpg"` (or any `https://` URL) in the seed file or the `events` table. Use 16:9 images (e.g. 1280×720). Old databases are upgraded automatically on the next start; to reseed from scratch delete `backend/smartevent.db`.

## Project layout
```
backend/app/  main.py config.py database.py models.py schemas.py security.py deps.py seed.py
              routers/  auth events bookings payments tickets notifications
              services/ payment_gateway payment_service booking_service ticket_service qr notify scheduler
frontend/src/ App.jsx api.js context/AuthContext.jsx
              components/ Navbar EventCard TicketCard NotificationDropdown ProtectedRoute
              pages/ Register Login Home EventDetails Payment BookingConfirmation BookingHistory PaymentHistory Tickets Notifications
```
