import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, allowedTypes }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return null; // prevent flicker during load

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  const userType = user.employee_type?.toLowerCase();

  // Debugging safety
  if (!userType) {
    console.warn("User type undefined for:", user);
    return <Navigate to="/login" replace />;
  }

  // Deny if employee_type not allowed
  if (!allowedTypes.includes(userType)) {
    console.error(
      `Access denied: user type "${userType}" not in allowedTypes: [${allowedTypes}]`
    );
    return <Navigate to="/login" replace />;
  }

  return children;
}
