/**
 * Configuración del servidor — Admin only.
 * Ruta: /admin/config
 * Servicios, SSL, SMTP, métricas, backups.
 */
export default function ServerConfig() {
  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ color: '#1565C0' }}>⚙️ Configuración del Servidor</h1>
      <p style={{ color: '#666' }}>Estado de servicios y configuración del sistema</p>

      {/* Estado de servicios */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginTop: 24 }}>
        <ServiceCard name="API Backend" status="running" port="8000" />
        <ServiceCard name="PostgreSQL" status="running" port="5432" />
        <ServiceCard name="Redis" status="running" port="6379" />
        <ServiceCard name="InfluxDB" status="running" port="8086" />
        <ServiceCard name="MQTT (Mosquitto)" status="running" port="1883" />
        <ServiceCard name="Nginx" status="running" port="443" />
      </div>

      {/* Configuración */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginTop: 32 }}>
        <ConfigSection title="🌐 Dominio y SSL" items={[
          'Dominio: echosmart.local',
          'SSL: Let\'s Encrypt (auto-renew)',
          'Certificado válido hasta: N/A',
        ]} />
        <ConfigSection title="📧 SMTP" items={[
          'Servidor: No configurado',
          'Puerto: 587',
          'TLS: Habilitado',
        ]} />
        <ConfigSection title="💾 Backups" items={[
          'Último backup: Nunca',
          'Frecuencia: Diario',
          'Retención: 30 días',
        ]} />
        <ConfigSection title="📊 Métricas" items={[
          'CPU: N/A',
          'RAM: N/A',
          'Disco: N/A',
          'Conexiones activas: 0',
        ]} />
      </div>

      {/* Acciones */}
      <div style={{ marginTop: 32, display: 'flex', gap: 12 }}>
        <button style={btnStyle('#2E7D32')}>💾 Backup Manual</button>
        <button style={btnStyle('#F57F17')}>🔄 Reiniciar Servicios</button>
        <button style={btnStyle('#1565C0')}>📋 Ver Logs</button>
      </div>
    </div>
  );
}

function ServiceCard({ name, status, port }) {
  const color = status === 'running' ? '#2E7D32' : '#C62828';
  return (
    <div style={{
      background: '#fff', borderRadius: 8, padding: 16,
      border: '1px solid #e0e0e0',
    }}>
      <div style={{ fontWeight: 'bold', color: '#333' }}>{name}</div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <span style={{ fontSize: 12, color }}>{status === 'running' ? '🟢 Running' : '🔴 Stopped'}</span>
        <span style={{ fontSize: 12, color: '#999' }}>:{port}</span>
      </div>
    </div>
  );
}

function ConfigSection({ title, items }) {
  return (
    <div style={{ background: '#f5f5f5', borderRadius: 8, padding: 16 }}>
      <h4 style={{ margin: '0 0 8px 0' }}>{title}</h4>
      {items.map((item, i) => (
        <div key={i} style={{ fontSize: 13, color: '#666', marginTop: 4 }}>{item}</div>
      ))}
    </div>
  );
}

function btnStyle(bg) {
  return {
    padding: '10px 20px', backgroundColor: bg, color: '#fff',
    border: 'none', borderRadius: 6, fontSize: 14, cursor: 'pointer',
  };
}
