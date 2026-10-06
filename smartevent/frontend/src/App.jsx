import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Register from "./pages/Register.jsx";
import Login from "./pages/Login.jsx";
import Home from "./pages/Home.jsx";
import EventDetails from "./pages/EventDetails.jsx";
import Payment from "./pages/Payment.jsx";
import BookingConfirmation from "./pages/BookingConfirmation.jsx";
import BookingHistory from "./pages/BookingHistory.jsx";
import PaymentHistory from "./pages/PaymentHistory.jsx";
import Tickets from "./pages/Tickets.jsx";
import Notifications from "./pages/Notifications.jsx";

export default function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/events/:id" element={<EventDetails />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/payment/:bookingId" element={<ProtectedRoute><Payment /></ProtectedRoute>} />
          <Route path="/booking-confirmation/:bookingId" element={<ProtectedRoute><BookingConfirmation /></ProtectedRoute>} />
          <Route path="/bookings" element={<ProtectedRoute><BookingHistory /></ProtectedRoute>} />
          <Route path="/payments" element={<ProtectedRoute><PaymentHistory /></ProtectedRoute>} />
          <Route path="/tickets" element={<ProtectedRoute><Tickets /></ProtectedRoute>} />
          <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}
