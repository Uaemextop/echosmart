/**
 * Sistema de ventas — Admin only.
 * Ruta: /admin/sales
 * Pedidos, inventario, reportes de ventas.
 */
export default function Sales() {
  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ color: '#1565C0' }}>💰 Ventas</h1>
      <p style={{ color: '#666' }}>Gestiona pedidos, inventario y reportes de ventas</p>

      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginTop: 24 }}>
        <KpiCard label="Ventas del Mes" value="$0" />
        <KpiCard label="Kits Vendidos" value="0" />
        <KpiCard label="Kits en Stock" value="0" />
        <KpiCard label="Clientes Activos" value="0" />
      </div>

      {/* Pedidos recientes */}
      <div style={{ marginTop: 32 }}>
        <h3>Pedidos Recientes</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f0f0f0' }}>
              <th style={thStyle}>Pedido #</th>
              <th style={thStyle}>Cliente</th>
              <th style={thStyle}>Kit</th>
              <th style={thStyle}>Cantidad</th>
              <th style={thStyle}>Total</th>
              <th style={thStyle}>Estado</th>
              <th style={thStyle}>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={7} style={{ padding: 24, textAlign: 'center', color: '#999' }}>
                No hay pedidos registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function KpiCard({ label, value }) {
  return (
    <div style={{ background: '#fff', borderRadius: 8, padding: 16, border: '1px solid #e0e0e0' }}>
      <div style={{ fontSize: 12, color: '#666' }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 'bold', color: '#333', marginTop: 4 }}>{value}</div>
    </div>
  );
}

const thStyle = { padding: 10, textAlign: 'left', borderBottom: '2px solid #ddd', fontSize: 12 };
