import { useEffect, useState } from 'react';
import { getIssues, getPRs, getCI, getBusFactor } from '../api';
import StatCard from '../components/StatCard';
import Card from '../components/Card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#e53e3e','#ed8936','#ecc94b','#48bb78','#4299e1','#9f7aea'];

export default function Overview() {
  const [issues, setIssues] = useState([]);
  const [prs,    setPRs]    = useState([]);
  const [ci,     setCI]     = useState([]);
  const [bus,    setBus]    = useState([]);

  useEffect(() => {
    getIssues().then(r => setIssues(r.data));
    getPRs().then(r => setPRs(r.data));
    getCI().then(r => setCI(r.data));
    getBusFactor().then(r => setBus(r.data));
  }, []);

  const totalOpen   = issues.reduce((s, r) => s + r.open, 0);
  const totalMerged = prs.reduce((s, r) => s + r.merged, 0);
  const totalOpenPR = prs.reduce((s, r) => s + r.open, 0);
  const avgMerge    = prs.length
    ? (prs.reduce((s,r) => s + r.avg_cycle_days, 0) / prs.length).toFixed(1)
    : '—';
  const ciPass = ci.length ? ci[0].pass_rate : '—';

  return (
    <div>
      <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20, color: '#e2e8f0' }}>
        ROCm Engineering Health
      </h1>

      {/* Stat row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 12, marginBottom: 24 }}>
        <StatCard label="Repositories" value={issues.length} sub="tracked" />
        <StatCard label="Open Issues"  value={totalOpen}  color="#e53e3e" />
        <StatCard label="PRs Waiting"  value={totalOpenPR} color="#ed8936" />
        <StatCard label="Avg Merge"    value={`${avgMerge}d`} color="#48bb78" />
        <StatCard label="CI Pass Rate" value={`${ciPass}%`}
          color={ciPass < 50 ? '#e53e3e' : '#48bb78'} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Open Issues by repo */}
        <Card title="Open Issues by Repository">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={issues} layout="vertical"
              margin={{ left: 80, right: 20, top: 4, bottom: 4 }}>
              <XAxis type="number" tick={{ fill: '#718096', fontSize: 11 }} />
              <YAxis type="category" dataKey="repo"
                tick={{ fill: '#a0aec0', fontSize: 11 }}
                tickFormatter={v => v.replace('ROCm/','')} width={80} />
              <Tooltip contentStyle={{ background:'#1a1d27', border:'1px solid #2d3748',
                borderRadius:6, fontSize:12 }} />
              <Bar dataKey="open" radius={[0,4,4,0]}>
                {issues.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Bus Factor */}
        <Card title="Bus Factor — Top-3 Contributor Concentration">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={bus} layout="vertical"
              margin={{ left: 80, right: 20, top: 4, bottom: 4 }}>
              <XAxis type="number" domain={[0,100]} unit="%" tick={{ fill:'#718096', fontSize:11 }} />
              <YAxis type="category" dataKey="repo"
                tick={{ fill:'#a0aec0', fontSize:11 }}
                tickFormatter={v => v.replace('ROCm/','')} width={80} />
              <Tooltip formatter={v => `${v}%`}
                contentStyle={{ background:'#1a1d27', border:'1px solid #2d3748',
                  borderRadius:6, fontSize:12 }} />
              <Bar dataKey="top3_pct" radius={[0,4,4,0]}>
                {bus.map((r,i) => (
                  <Cell key={i} fill={r.top3_pct > 70 ? '#e53e3e' : r.top3_pct > 50 ? '#ed8936' : '#48bb78'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#4a5568', marginTop: 8 }}>
            Red &gt;70% · Orange &gt;50% · Green = healthy distribution
          </div>
        </Card>
      </div>
    </div>
  );
}
