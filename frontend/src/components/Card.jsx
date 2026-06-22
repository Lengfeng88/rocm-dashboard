export default function Card({ title, children, style = {} }) {
  return (
    <div style={{
      background: '#1a1d27', border: '1px solid #2d3748',
      borderRadius: 10, padding: 20, ...style
    }}>
      {title && <div style={{ fontSize: 12, fontWeight: 600, color: '#718096',
        textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>{title}</div>}
      {children}
    </div>
  );
}
