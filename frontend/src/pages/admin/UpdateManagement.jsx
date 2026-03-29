/**
 * Gestión de actualizaciones Cosmuodate — Admin only.
 * Ruta: /admin/updates
 * Publicar, desplegar y monitorear actualizaciones.
 */
export default function UpdateManagement() {
  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ color: '#1565C0' }}>📦 Actualizaciones (Cosmuodate)</h1>
      <p style={{ color: '#666' }}>Publica y despliega actualizaciones para EchoPy, apps y sensores</p>

      {/* Componentes */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginTop: 24 }}>
        <ComponentCard name="Gateway (EchoPy)" version="1.0.0" channel="stable" status="✅ Al día" />
        <ComponentCard name="Sistema Base" version="1.0.0" channel="stable" status="✅ Al día" />
        <ComponentCard name="App Web" version="1.0.0" channel="stable" status="✅ Al día" />
        <ComponentCard name="App Mobile" version="1.0.0" channel="stable" status="✅ Al día" />
        <ComponentCard name="App Desktop" version="1.0.0" channel="stable" status="✅ Al día" />
        <ComponentCard name="Sensores" version="1.0.0" channel="stable" status="✅ Al día" />
      </div>

      {/* Publicar nueva actualización */}
      <div style={{ background: '#f5f5f5', borderRadius: 12, padding: 20, marginTop: 32 }}>
        <h3>Publicar Nueva Actualización</h3>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 12 }}>
          <select style={selectStyle}>
            <option>gateway</option>
            <option>system</option>
            <option>app-web</option>
            <option>app-mobile</option>
            <option>app-desktop</option>
            <option>sensor</option>
          </select>
          <input type="text" placeholder="Versión (e.g., 1.1.0)" style={selectStyle} />
          <select style={selectStyle}>
            <option value="stable">Estable</option>
            <option value="beta">Beta</option>
          </select>
          <button style={buttonStyle}>Publicar</button>
        </div>
      </div>

      {/* Historial */}
      <div style={{ marginTop: 32 }}>
        <h3>Historial de Actualizaciones</h3>
        <p style={{ color: '#999' }}>No hay actualizaciones publicadas aún.</p>
      </div>
    </div>
  );
}

function ComponentCard({ name, version, channel, status }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 8, padding: 16,
      border: '1px solid #e0e0e0',
    }}>
      <div style={{ fontWeight: 'bold', color: '#333' }}>{name}</div>
      <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>v{version} ({channel})</div>
      <div style={{ fontSize: 12, marginTop: 8 }}>{status}</div>
    </div>
  );
}

const selectStyle = { padding: 10, border: '1px solid #ddd', borderRadius: 6, fontSize: 14 };
const buttonStyle = {
  padding: '10px 20px', backgroundColor: '#1565C0', color: '#fff',
  border: 'none', borderRadius: 6, fontSize: 14, cursor: 'pointer',
};
