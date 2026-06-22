import { useEffect, useState } from 'react';
import { getIssues } from '../api';
import Card from '../components/Card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function Issues() {
  const [data, setData] = useState([]);
  useEffect(() => { getIssues().then(r => setData(r.data)); }, []);

  return (
    <div>
      <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20 }}>Issue Analysis</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card title="Open vs Closed Issues">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data} margin={{ left: 0, right: 16, top: 4, bottom: 40 }}>
              <XAxis dataKey="repo" tick={{ fill:'#a0aec0', fontSize:11 }}
                tickFormatter={v => v.replace('ROCm/','')} angle={-30} textAnchor="end" />
              <YAxis tick={{ fill:'#718096', fontSize:11 }} />
              <Tooltip contentStyle={{ background:'#1a1d27', border:'1px solid #2d3748',
                borderRadius:6, fontSize:12 }} />
              <Legend wrapperStyle={{ fontSize:12, paddingTop:8 }} />
              <Bar dataKey="open"   name="Open"   fill="#e53e3e" radius={[4,4,0,0]} />
              <Bar dataKey="closed" name="Closed" fill="#4299e1" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Avg Resolution Time (days)">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data} margin={{ left: 0, right: 16, top: 4, bottom: 40 }}>
              <XAxis dataKey="repo" tick={{ fill:'#a0aec0', fontSize:11 }}
                tickFormatter={v => v.replace('ROCm/','')} angle={-30} textAnchor="end" />
              <YAxis tick={{ fill:'#718096', fontSize:11 }} />
              <Tooltip contentStyle={{ background:'#1a1d27', border:'1px solid #2d3748',
                borderRadius:6, fontSize:12 }} />
              <Bar dataKey="avg_resolve_days" name="Avg Days" fill="#9f7aea" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Issue Summary Table">
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
          <thead>
            <tr style={{ borderBottom:'1px solid #2d3748' }}>
              {['Repository','Open','Closed','Avg Resolve (days)'].map(h => (
                <th key={h} style={{ textAlign:'left', padding:'8px 12px',
                  color:'#718096', fontWeight:500, fontSize:11 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((r,i) => (
              <tr key={i} style={{ borderBottom:'1px solid #1e2433' }}>
                <td style={{ padding:'10px 12px', color:'#a0aec0' }}>{r.repo.replace('ROCm/','')}</td>
                <td style={{ padding:'10px 12px' }}>
                  <span style={{ color: r.open > 5 ? '#e53e3e' : '#48bb78',
                    fontWeight:600 }}>{r.open}</span>
                </td>
                <td style={{ padding:'10px 12px', color:'#e2e8f0' }}>{r.closed}</td>
                <td style={{ padding:'10px 12px', color:'#e2e8f0' }}>{r.avg_resolve_days}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
