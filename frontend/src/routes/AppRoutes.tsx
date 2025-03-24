import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'
import OrgDashboard from '../../app/org/dashboard/page'
import StudentDashboard from '../../app/student/dashboard/page'
import FacultyDashboard from '../../app/faculty/dashboard/page'
import AdminPanel from '../pages/AdminPanel'

export default function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/org/dashboard" element={<OrgDashboard />} />
        <Route path="/student/dashboard" element={<StudentDashboard />} />
        <Route path="/faculty/dashboard" element={<FacultyDashboard />} />
        <Route path="/admin/dashboard" element={<AdminPanel />} />
      </Routes>
    </Router>
  )
}
