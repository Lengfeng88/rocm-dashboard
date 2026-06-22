import { useState } from 'react';
import axios from 'axios';
import Card from '../components/Card';

export default function AI() {
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [savedTo, setSavedTo] = useState('');

  const generate = async () => {
    setLoading(true);
    setReport('');
    try {
      const r = await axios.get('http://localhost:8000/api/ai/weekly-summary');
      setReport(r.data.report);
      setSavedTo(r.data.saved_to);
    } catch (e) {
      setReport('Error: ' + e.message);
    }
    setLoading(false);
  };

  // Simple markdown → HTML (bold, headers, bullets)
  const renderMd = (md) => md
    .split('\n')
    .map((line, i) => {
      if (line.startsWith('## '))
        return <div key={i} style={{ fontSize:14, fontWeight:700, color:'#e2e8f0',
          margin:'20px 0 8px', borderBottom:'1px solid #2d3748', paddingBottom:4 }}>
          {line.replace('## ','')}
        </div>;
      if (line.startsWith('- '))
        return <div key={i} style={{ display:'flex', gap:8, margin:'4px 0',
          color:'#a0aec0', fontSize:13, lineHeight:1.6 }}>
          <span style={{ color:'#4a5568', flexShrink:0 }}>•</span>
          <span dangerouslySetInnerHTML={{ __html:
            line.slice(2).replace(/\*\*(.+?)\*\*/g,'<strong style="color:#e2e8f0">$1</strong>')
          }}/>
        </div>;
      if (line.match(/^\d\./))
        return <div key={i} style={{ margin:'4px 0', color:'#a0aec0',
          fontSize:13, lineHeight:1.6 }}
          dangerouslySetInnerHTML={{ __html:
            line.replace(/\*\*(.+?)\*\*/g,'<strong style="color:#e2e8f0">$1</strong>')
          }}/>;
      if (line.trim() === '') return <div key={i} style={{ height:4 }} />;
      return <div key={i} style={{ color:'#a0aec0', fontSize:13, lineHeight:1.6 }}
        dangerouslySetInnerHTML={{ __html:
          line.replace(/\*\*(.+?)\*\*/g,'<strong style="color:#e2e8f0">$1</strong>')
        }}/>;
    });

  return (
    <div>
      <div style={{ display:'flex', alignItems:'center', gap:16, marginBottom:20 }}>
        <h2 style={{ fontSize:16, fontWeight:700 }}>AI Weekly Summary</h2>
        <button onClick={generate} disabled={loading} style={{
          padding:'7px 18px', borderRadius:6, border:'none', cursor:'pointer',
          background: loading ? '#2d3748' : '#e53e3e',
          color:'#fff', fontWeight:600, fontSize:13,
        }}>
          {loading ? 'Generating…' : '⚡ Generate Report'}
        </button>
        {savedTo && <span style={{ fontSize:11, color:'#4a5568' }}>✅ {savedTo}</span>}
      </div>

      {!report && !loading && (
        <div style={{ background:'#1a1d27', border:'1px solid #2d3748', borderRadius:10,
          padding:'40px 24px', textAlign:'center', color:'#4a5568' }}>
          Click "Generate Report" to call DeepSeek AI with live KPI data
        </div>
      )}

      {loading && (
        <div style={{ background:'#1a1d27', border:'1px solid #2d3748', borderRadius:10,
          padding:'40px 24px', textAlign:'center', color:'#718096' }}>
          Fetching KPIs from database and calling DeepSeek…
        </div>
      )}

      {report && (
        <Card>
          <div style={{ lineHeight:1.7 }}>{renderMd(report)}</div>
        </Card>
      )}
    </div>
  );
}
