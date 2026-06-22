export default function StatCard({ label, value, sub, color = '#e2e8f0' }) {
  return (
    <div style={{ background: '#1a1d27', border: '1px solid #2d3748',
      borderRadius: 10, padding: '16px 20px' }}>
      <div style={{ fontSize: 11, color: '#718096', marginBottom: 6,
        textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 700, color }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: '#4a5568', marginTop: 4 }}>{sub}</div>}
    </div>
  );
}
