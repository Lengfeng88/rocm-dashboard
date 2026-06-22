import { useEffect, useState } from 'react';
import { getPRs } from '../api';
import Card from '../components/Card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#e53e3e','#ed8936','#ecc94b','#48bb78','#4299e1','#9f7aea'];

export default function PRs() {
  const [data, setData] = useState([]);
  useEffect(() => { getPRs().then(r => setData(r.data)); }, []);

  return (
    <div>
      <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20 }}>PR Health</h2>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, marginBottom:16 }}>
        <Card title="Avg PR Cycle Time (days)">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data} margin={{ left:0, right:16, top:4, bottom:40 }}>
              <XAxis dataKey="repo" tick={{ fill:'#a0aec0', fontSize:11 }}
                tickFormatter={v => v.replace('ROCm/','')} angle={-30} textAnchor="end" />
              <YAxis tick={{ fill:'#718096', fontSize:11 }} />
              <Tooltip contentStyle={{ background:'#1a1d27', border:'1px solid #2d3748',
                borderRadius:6, fontSize:12 }} />
              <Bar dataKey="avg_cycle_days" name="Days" radius={[4,4,0,0]}>
                {data.map((r,i) => (
                  <Cell key={i} fill={r.avg_cycle_days > 10 ? '#e53e3e' :
                    r.avg_cycle_days > 5 ? '#ed8936' : '#48bb78'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Total Merged PRs">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data} margin={{ left:0, right:16, top:4, bottom:40 }}>
              <XAxis dataKey="repo" tick={{ fill:'#a0aec0', fontSize:11 }}
                tickFormatter={v => v.replace('ROCm/','')} angle={-30} textAnchor="end" />
              <YAxis tick={{ fill:'#718096', fontSize:11 }} />
              <Tooltip contentStyle={{ background:'#1a1d27', border:'1px solid #2d3748',
                borderRadius:6, fontSize:12 }} />
              <Bar dataKey="merged" name="Merged" radius={[4,4,0,0]}>
                {data.map((_,i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="PR Pipeline Table">
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
          <thead>
            <tr style={{ borderBottom:'1px solid #2d3748' }}>
              {['Repository','Open PRs','Merged','Avg Cycle (days)','Status'].map(h => (
                <th key={h} style={{ textAlign:'left', padding:'8px 12px',
                  color:'#718096', fontWeight:500, fontSize:11 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((r,i) => {
              const status = r.avg_cycle_days > 10 ? ['Slow','#e53e3e'] :
                             r.avg_cycle_days > 5  ? ['Watch','#ed8936'] :
                                                     ['Healthy','#48bb78'];
              return (
                <tr key={i} style={{ borderBottom:'1px solid #1e2433' }}>
                  <td style={{ padding:'10px 12px', color:'#a0aec0' }}>{r.repo.replace('ROCm/','')}</td>
                  <td style={{ padding:'10px 12px', color:'#ed8936', fontWeight:600 }}>{r.open}</td>
                  <td style={{ padding:'10px 12px', color:'#e2e8f0' }}>{r.merged}</td>
                  <td style={{ padding:'10px 12px', color:'#e2e8f0' }}>{r.avg_cycle_days}</td>
                  <td style={{ padding:'10px 12px' }}>
                    <span style={{ background: status[1]+'22', color: status[1],
                      padding:'2px 8px', borderRadius:4, fontSize:11, fontWeight:600 }}>
                      {status[0]}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
