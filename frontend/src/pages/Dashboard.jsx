import { useEffect, useState } from 'react';
import API from '../services/api';
import StatsChart from '../components/StatsChart';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [students, setStudents] = useState([]);
  const [orgs, setOrgs] = useState([]);
  const [grades, setGrades] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const userRes = await API.get('auth/user/');
      setUser(userRes.data);
      const sRes = await API.get('students/');
      setStudents(sRes.data);
      const oRes = await API.get('organizations/');
      setOrgs(oRes.data);
      const gRes = await API.get('grades/');
      setGrades(gRes.data);
    };
    fetchData();
  }, []);

  const matchedCount = students.filter(s => s.matched).length;
  const unmatchedCount = students.length - matchedCount;
  const avgScore = grades.length ? grades.reduce((a, b) => a + b.score, 0) / grades.length : 0;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Welcome {user?.username}</h1>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-lg font-semibold">Dashboard Overview</h2>
        <ul className="mt-2 space-y-1">
          <li>Total Students: {students.length}</li>
          <li>Matched: {matchedCount}</li>
          <li>Unmatched: {unmatchedCount}</li>
          <li>Organizations: {orgs.length}</li>
          <li>Grades: {grades.length} (avg: {avgScore.toFixed(2)})</li>
        </ul>
      </div>
      <div className="bg-white p-4 rounded shadow">
        <StatsChart matched={matchedCount} unmatched={unmatchedCount} />
      </div>
    </div>
  );
}