/**
 * Gestión de números de serie — Admin only.
 * Ruta: /admin/serials
 * Generar, listar, revocar, exportar seriales para kits EchoPy.
 */
export default function SerialCodes() {
  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ color: '#1565C0' }}>🔑 Números de Serie</h1>
      <p style={{ color: '#666' }}>Genera y gestiona los seriales para kits EchoPy</p>

      {/* Generar seriales */}
      <div style={{ background: '#f5f5f5', borderRadius: 12, padding: 20, marginTop: 24 }}>
        <h3>Generar Nuevos Seriales</h3>
        <div style={{ display: 'flex', gap: 12, alignItems: 'end' }}>
          <div>
            <label style={{ fontSize: 12, color: '#666' }}>Cantidad</label>
            <input type="number" defaultValue={10} min={1} max={1000} style={inputStyle} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#666' }}>Prefijo</label>
            <input type="text" defaultValue="ES" style={inputStyle} />
          </div>
          <button style={buttonStyle}>Generar</button>
          <button style={{ ...buttonStyle, backgroundColor: '#666' }}>Exportar CSV</button>
        </div>
      </div>

      {/* Estadísticas */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginTop: 24 }}>
        <StatCard label="Total Generados" value="0" color="#1565C0" />
        <StatCard label="Disponibles" value="0" color="#2E7D32" />
        <StatCard label="Registrados" value="0" color="#F57F17" />
        <StatCard label="Revocados" value="0" color="#C62828" />
      </div>

      {/* Tabla de seriales */}
      <div style={{ marginTop: 24 }}>
        <h3>Seriales Recientes</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f0f0f0' }}>
              <th style={thStyle}>Serial</th>
              <th style={thStyle}>Estado</th>
              <th style={thStyle}>Usuario</th>
              <th style={thStyle}>EchoPy</th>
              <th style={thStyle}>Fecha</th>
              <th style={thStyle}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={6} style={{ padding: 24, textAlign: 'center', color: '#999' }}>
                No hay seriales generados aún. Genera un lote para comenzar.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div style={{ background: '#fff', borderRadius: 8, padding: 16, border: '1px solid #e0e0e0' }}>
      <div style={{ fontSize: 12, color: '#666' }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 'bold', color, marginTop: 4 }}>{value}</div>
    </div>
  );
}

const inputStyle = { padding: 10, border: '1px solid #ddd', borderRadius: 6, fontSize: 14, width: 120 };
const buttonStyle = {
  padding: '10px 20px', backgroundColor: '#1565C0', color: '#fff',
  border: 'none', borderRadius: 6, fontSize: 14, cursor: 'pointer',
};
const thStyle = { padding: 10, textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: 13 };
