import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LoanApplication from './pages/LoanApplication';
import LoanStatus from './pages/LoanStatus';
import Prediction from './pages/Prediction';
import PrivateRoute from './components/PrivateRoute';
import { isAuthenticated } from './services/authService';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to={isAuthenticated() ? '/dashboard' : '/login'} replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/apply" element={<PrivateRoute><LoanApplication /></PrivateRoute>} />
        <Route path="/status" element={<PrivateRoute><LoanStatus /></PrivateRoute>} />
        <Route path="/predict" element={<PrivateRoute><Prediction /></PrivateRoute>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
