import { useEffect, useState } from 'react';
import axios from 'axios';
import Card from '../components/Card';

export default function CI() {
  const [stability, setStability] = useState([]);
  const [coverage,  setCoverage]  = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/ci/stability').then(r => setStability(r.data));
    axios.get('http://localhost:8000/api/ci/coverage').then(r => setCoverage(r.data));
  }, []);

  return (
    <div>
      <h2 style={{ fontSize:16, fontWeight:700, marginBottom:20 }}>CI Stability</h2>

      {/* Coverage overview */}
      <Card title="CI Coverage — GitHub Actions vs Internal CI" style={{ marginBottom:16 }}>
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
          <thead>
            <tr style={{ borderBottom:'1px solid #2d3748' }}>
              {['Repository','Real CI Runs','Bot Runs','Total','CI Type'].map(h => (
                <th key={h} style={{ textAlign:'left', padding:'7px 12px',
                  color:'#718096', fontWeight:500, fontSize:11 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {coverage.map((r,i) => {
              const hasCI = r.real_ci_runs > 0;
              return (
                <tr key={i} style={{ borderBottom:'1px solid #1e2433' }}>
                  <td style={{ padding:'9px 12px', color:'#a0aec0' }}>
                    {r.repo.replace('ROCm/','')}
                  </td>
                  <td style={{ padding:'9px 12px',
                    color: hasCI ? '#48bb78' : '#4a5568',
                    fontWeight: hasCI ? 600 : 400 }}>
                    {r.real_ci_runs}
                  </td>
                  <td style={{ padding:'9px 12px', color:'#4a5568' }}>{r.bot_runs}</td>
                  <td style={{ padding:'9px 12px', color:'#718096' }}>{r.total_runs}</td>
                  <td style={{ padding:'9px 12px' }}>
                    {hasCI
                      ? <span style={{ background:'#48bb7822', color:'#48bb78',
                          padding:'2px 8px', borderRadius:4, fontSize:11, fontWeight:600 }}>
                          GitHub Actions
                        </span>
                      : <span style={{ background:'#4a556822', color:'#718096',
                          padding:'2px 8px', borderRadius:4, fontSize:11 }}>
                          Internal only (Jenkins)
                        </span>
                    }
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div style={{ marginTop:12, fontSize:11, color:'#4a5568', lineHeight:1.6 }}>
          💡 MIOpen, rocSPARSE, rocFFT, rocBLAS use AMD internal CI (Jenkins/BuildKite) —
          not visible via GitHub API. Only HIP and RCCL expose CI status publicly.
        </div>
      </Card>

      {/* Pass rate for repos with real CI */}
      <Card title="Pass Rate — GitHub Actions only (HIP & RCCL)">
        {stability.length === 0
          ? <div style={{ color:'#4a5568', padding:'12px 0' }}>Loading…</div>
          : stability.map((r,i) => {
              const pct   = r.pass_rate;
              const color = pct >= 80 ? '#48bb78' : pct >= 40 ? '#ed8936' : '#e53e3e';
              return (
                <div key={i} style={{ marginBottom:20 }}>
                  <div style={{ display:'flex', justifyContent:'space-between',
                    marginBottom:6, fontSize:13 }}>
                    <span style={{ color:'#a0aec0', fontWeight:500 }}>
                      {r.repo.replace('ROCm/','')}
                    </span>
                    <span style={{ color, fontWeight:700 }}>{pct}% pass</span>
                  </div>
                  <div style={{ background:'#2d3748', borderRadius:4, height:12 }}>
                    <div style={{ width:`${pct}%`, background:color,
                      borderRadius:4, height:12, transition:'width 0.6s' }} />
                  </div>
                  <div style={{ display:'flex', gap:20, marginTop:6,
                    fontSize:11, color:'#4a5568' }}>
                    <span>Total: <b style={{ color:'#718096' }}>{r.total_runs}</b></span>
                    <span style={{ color:'#48bb78' }}>✓ {r.passed} passed</span>
                    <span style={{ color:'#e53e3e' }}>✗ {r.failed} failed</span>
                    <span>Median: <b style={{ color:'#718096' }}>{r.median_min} min</b></span>
                  </div>

                  {/* HIP specific insight */}
                  {r.repo === 'ROCm/hip' && (
                    <div style={{ marginTop:8, padding:'8px 12px', background:'#2d1515',
                      border:'1px solid #e53e3e44', borderRadius:6,
                      fontSize:11, color:'#fc8181', lineHeight:1.6 }}>
                      ⚠️ All 22 runs failed with median 0.6 min — indicates immediate
                      compile/config failure, not test failure. Likely a TheRock or
                      HIP runtime dependency issue introduced recently.
                    </div>
                  )}
                  {r.repo === 'ROCm/rccl' && (
                    <div style={{ marginTop:8, padding:'8px 12px', background:'#2d2015',
                      border:'1px solid #ed893644', borderRadius:6,
                      fontSize:11, color:'#fbd38d', lineHeight:1.6 }}>
                      ⚠️ 25% pass rate over 48 runs — failures at ~3.6 min median suggest
                      early test suite or environment setup failure.
                    </div>
                  )}
                </div>
              );
            })
        }
      </Card>
    </div>
  );
}
