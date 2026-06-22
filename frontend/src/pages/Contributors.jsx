import { useEffect, useState } from 'react';
import { getContributors, getBusFactor } from '../api';
import Card from '../components/Card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function Contributors() {
  const [ranking, setRanking] = useState([]);
  const [bus,     setBus]     = useState([]);

  useEffect(() => {
    getContributors().then(r => setRanking(r.data));
    getBusFactor().then(r => setBus(r.data));
  }, []);

  const top10 = ranking.slice(0, 10);

  return (
    <div>
      <h2 style={{ fontSize:16, fontWeight:700, marginBottom:20 }}>Contributors</h2>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, marginBottom:16 }}>
        <Card title="Top 10 Contributors (all-time commits)">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={top10} layout="vertical"
              margin={{ left:80, right:20, top:4, bottom:4 }}>
              <XAxis type="number" tick={{ fill:'#718096', fontSize:11 }} />
              <YAxis type="category" dataKey="author"
                tick={{ fill:'#a0aec0', fontSize:11 }} width={80} />
              <Tooltip contentStyle={{ background:'#1a1d27', border:'1px solid #2d3748',
                borderRadius:6, fontSize:12 }} />
              <Bar dataKey="commits" name="Commits" fill="#9f7aea" radius={[0,4,4,0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Bus Factor — Knowledge Concentration Risk">
          {bus.map((r,i) => {
            const color = r.top3_pct > 70 ? '#e53e3e' : r.top3_pct > 50 ? '#ed8936' : '#48bb78';
            return (
              <div key={i} style={{ marginBottom:14 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:5, fontSize:13 }}>
                  <span style={{ color:'#a0aec0' }}>{r.repo.replace('ROCm/','')}</span>
                  <span style={{ color, fontWeight:700 }}>{r.top3_pct}%</span>
                </div>
                <div style={{ background:'#2d3748', borderRadius:4, height:8 }}>
                  <div style={{ width:`${r.top3_pct}%`, background:color,
                    borderRadius:4, height:8 }} />
                </div>
                <div style={{ fontSize:11, color:'#4a5568', marginTop:4 }}>
                  {r.top3_commits} / {r.total_commits} commits by top 3
                </div>
              </div>
            );
          })}
        </Card>
      </div>

      <Card title="Full Contributor Ranking">
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
          <thead>
            <tr style={{ borderBottom:'1px solid #2d3748' }}>
              {['#','Author','Repos','Commits'].map(h => (
                <th key={h} style={{ textAlign:'left', padding:'8px 12px',
                  color:'#718096', fontWeight:500, fontSize:11 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ranking.map((r,i) => (
              <tr key={i} style={{ borderBottom:'1px solid #1e2433' }}>
                <td style={{ padding:'8px 12px', color:'#4a5568' }}>{i+1}</td>
                <td style={{ padding:'8px 12px', color:'#e2e8f0', fontWeight: i<3 ? 600:400 }}>
                  {i === 0 && '🥇 '}{i === 1 && '🥈 '}{i === 2 && '🥉 '}{r.author}
                </td>
                <td style={{ padding:'8px 12px', color:'#a0aec0' }}>{r.repos}</td>
                <td style={{ padding:'8px 12px', color:'#9f7aea', fontWeight:600 }}>{r.commits}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
