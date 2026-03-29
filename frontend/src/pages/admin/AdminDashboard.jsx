/**
 * Dashboard principal del administrador.
 * Ruta: /admin
 * Muestra resumen: EchoPys activos, seriales, ventas, actualizaciones.
 */
export default function AdminDashboard() {
  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ color: '#1565C0' }}>📊 Panel de Administración</h1>
      <p style={{ color: '#666' }}>Bienvenido al panel de control de EchoSmart</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16, marginTop: 24 }}>
        <Card title="🟢 EchoPys Activos" value="0" link="/admin/echopy" />
        <Card title="🔑 Seriales Disponibles" value="0" link="/admin/serials" />
        <Card title="📦 Actualizaciones" value="0" link="/admin/updates" />
        <Card title="💰 Ventas del Mes" value="$0" link="/admin/sales" />
        <Card title="👥 Usuarios" value="0" link="/admin/echopy" />
        <Card title="⚙️ Servidor" value="Healthy" link="/admin/config" />
      </div>

      <h2 style={{ marginTop: 32, color: '#333' }}>Accesos Rápidos</h2>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <a href="/admin/serials" style={linkStyle}>Generar Seriales</a>
        <a href="/admin/echopy" style={linkStyle}>Gestionar EchoPys</a>
        <a href="/admin/updates" style={linkStyle}>Publicar Actualización</a>
        <a href="/admin/sales" style={linkStyle}>Reportes de Ventas</a>
        <a href="/admin/config" style={linkStyle}>Configuración del Servidor</a>
      </div>
    </div>
  );
}

function Card({ title, value, link }) {
  return (
    <a href={link} style={{ textDecoration: 'none' }}>
      <div style={{
        background: '#f5f5f5', borderRadius: 12, padding: 20,
        border: '1px solid #e0e0e0', cursor: 'pointer',
      }}>
        <div style={{ fontSize: 14, color: '#666' }}>{title}</div>
        <div style={{ fontSize: 28, fontWeight: 'bold', color: '#333', marginTop: 8 }}>{value}</div>
      </div>
    </a>
  );
}

const linkStyle = {
  padding: '10px 20px', backgroundColor: '#1565C0', color: '#fff',
  borderRadius: 8, textDecoration: 'none', fontSize: 14,
};
