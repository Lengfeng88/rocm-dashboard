import { useState } from 'react';
import Overview   from './pages/Overview';
import Issues     from './pages/Issues';
import PRs        from './pages/PRs';
import CI         from './pages/CI';
import Contributors from './pages/Contributors';
import AI from './pages/AI';

const TABS = ['Overview', 'Issues', 'PRs', 'CI', 'Contributors', 'AI'];

export default function App() {
  const [tab, setTab] = useState('Overview');

  return (
    <div style={{ minHeight: '100vh', background: '#0f1117' }}>
      {/* Header */}
      <div style={{ background: '#1a1d27', borderBottom: '1px solid #2d3748', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 32, height: 52 }}>
          <span style={{ fontWeight: 700, fontSize: 15, color: '#e53e3e', letterSpacing: '0.02em' }}>
            ROCm Health
          </span>
          <nav style={{ display: 'flex', gap: 4 }}>
            {TABS.map(t => (
              <button key={t} onClick={() => setTab(t)} style={{
                padding: '6px 14px', borderRadius: 6, border: 'none', cursor: 'pointer',
                background: tab === t ? '#2d3748' : 'transparent',
                color: tab === t ? '#e2e8f0' : '#718096',
                fontWeight: tab === t ? 600 : 400, fontSize: 13,
              }}>{t}</button>
            ))}
          </nav>
        </div>
      </div>

      {/* Page */}
      <div style={{ padding: 24 }}>
        {tab === 'Overview'      && <Overview />}
        {tab === 'Issues'        && <Issues />}
        {tab === 'PRs'           && <PRs />}
        {tab === 'CI'            && <CI />}
        {tab === 'Contributors'  && <Contributors />}
        {tab === 'AI'           && <AI />}
      </div>
    </div>
  );
}
