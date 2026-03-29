/**
 * Gestión de dispositivos EchoPy — Admin only.
 * Ruta: /admin/echopy
 * Ver todos los EchoPys, info de debug, SSH remoto, suspend, reboot.
 */
export default function EchoPyManagement() {
  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ color: '#1565C0' }}>📟 Gestión de EchoPy</h1>
      <p style={{ color: '#666' }}>Administra todos los dispositivos EchoPy registrados</p>

      {/* Filtros */}
      <div style={{ display: 'flex', gap: 12, marginTop: 24, flexWrap: 'wrap' }}>
        <select style={selectStyle}>
          <option value="">Todos los estados</option>
          <option value="active">Activos</option>
          <option value="offline">Offline</option>
          <option value="suspended">Suspendidos</option>
          <option value="pending">Pendientes</option>
        </select>
        <input type="text" placeholder="Buscar por serial o nombre..." style={{ ...selectStyle, width: 250 }} />
      </div>

      {/* Tabla de EchoPys */}
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 16 }}>
        <thead>
          <tr style={{ background: '#f0f0f0' }}>
            <th style={thStyle}>Nombre</th>
            <th style={thStyle}>Serial</th>
            <th style={thStyle}>Estado</th>
            <th style={thStyle}>Usuario</th>
            <th style={thStyle}>IP</th>
            <th style={thStyle}>Firmware</th>
            <th style={thStyle}>Última conexión</th>
            <th style={thStyle}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colSpan={8} style={{ padding: 24, textAlign: 'center', color: '#999' }}>
              No hay dispositivos EchoPy registrados.
            </td>
          </tr>
        </tbody>
      </table>

      {/* Panel de acciones remotas (se muestra al seleccionar un EchoPy) */}
      <div style={{ background: '#f5f5f5', borderRadius: 12, padding: 20, marginTop: 32 }}>
        <h3>🔧 Acciones Remotas</h3>
        <p style={{ color: '#666', fontSize: 13 }}>
          Selecciona un EchoPy para ver diagnósticos y ejecutar acciones remotas.
        </p>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 12 }}>
          <button style={actionBtn('#2E7D32')}>📊 Diagnósticos</button>
          <button style={actionBtn('#1565C0')}>📋 Ver Logs</button>
          <button style={actionBtn('#F57F17')}>🔄 Reiniciar</button>
          <button style={actionBtn('#7B1FA2')}>💻 SSH Remoto</button>
          <button style={actionBtn('#C62828')}>⏸️ Suspender</button>
          <button style={actionBtn('#333')}>🔓 Desvincular</button>
        </div>
      </div>
    </div>
  );
}

const selectStyle = {
  padding: 10, border: '1px solid #ddd', borderRadius: 6, fontSize: 14,
};
const thStyle = { padding: 10, textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: 12 };

function actionBtn(bg) {
  return {
    padding: '8px 16px', backgroundColor: bg, color: '#fff',
    border: 'none', borderRadius: 6, fontSize: 13, cursor: 'pointer',
  };
}
