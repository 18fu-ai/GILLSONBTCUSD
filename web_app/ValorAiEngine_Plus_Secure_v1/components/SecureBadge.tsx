export default function SecureBadge() {
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      background: 'linear-gradient(120deg, rgba(15,120,255,0.15), rgba(0,200,160,0.12))',
      padding: '8px 12px',
      borderRadius: 9999,
      border: '1px solid rgba(255,255,255,0.15)'
    }}>
      <span style={{ width: 10, height: 10, borderRadius: 9999, background: '#30f5a4', boxShadow: '0 0 10px #30f5a4' }} />
      <span style={{ fontSize: 12, letterSpacing: 0.3 }}>Guardian Vault • Live</span>
    </div>
  );
}