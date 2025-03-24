import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

export default function StatsChart({ matched, unmatched }) {
  const data = [
    { name: 'Matched', value: matched },
    { name: 'Unmatched', value: unmatched },
  ];
  const COLORS = ['#4F2683', '#818284'];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" outerRadius={80} label dataKey="value">
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}