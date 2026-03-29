/**
 * Login exclusivo para administradores.
 * Ruta: /admin/login
 * Requiere rol admin + 2FA.
 */
export default function AdminLogin() {
  return (
    <div style={{ maxWidth: 420, margin: '100px auto', padding: 32 }}>
      <h1 style={{ textAlign: 'center', color: '#1565C0' }}>🔒 Administración</h1>
      <p style={{ textAlign: 'center', color: '#666' }}>EchoSmart — Panel de Control</p>

      <form style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 32 }}>
        <input type="email" placeholder="Email del administrador" style={inputStyle} />
        <input type="password" placeholder="Contraseña" style={inputStyle} />
        <input type="text" placeholder="Código 2FA (si habilitado)" style={inputStyle} />
        <button type="submit" style={buttonStyle}>Acceder</button>
      </form>
    </div>
  );
}

const inputStyle = {
  padding: 12, border: '1px solid #ddd', borderRadius: 8, fontSize: 16,
};

const buttonStyle = {
  padding: 14, backgroundColor: '#1565C0', color: '#fff',
  border: 'none', borderRadius: 8, fontSize: 16, fontWeight: 'bold', cursor: 'pointer',
};
