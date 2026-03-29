/**
 * Página de registro de usuario — requiere serial del kit.
 */
export default function Register() {
  return (
    <div style={{ maxWidth: 480, margin: '80px auto', padding: 32 }}>
      <h1 style={{ textAlign: 'center', color: '#2E7D32' }}>🌿 Registrar Kit</h1>
      <p style={{ textAlign: 'center', color: '#666' }}>
        Ingresa el número de serie de tu kit EchoPy para crear tu cuenta.
      </p>

      <form style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 32 }}>
        <div>
          <label style={{ fontWeight: 'bold', fontSize: 14 }}>Número de Serie</label>
          <input
            type="text"
            placeholder="ES-202603-0001"
            style={inputStyle}
          />
          <small style={{ color: '#999' }}>
            Encuentra el serial en la etiqueta dentro de tu kit.
          </small>
        </div>

        <div>
          <label style={{ fontWeight: 'bold', fontSize: 14 }}>Nombre completo</label>
          <input type="text" placeholder="Tu nombre" style={inputStyle} />
        </div>

        <div>
          <label style={{ fontWeight: 'bold', fontSize: 14 }}>Correo electrónico</label>
          <input type="email" placeholder="tu@email.com" style={inputStyle} />
        </div>

        <div>
          <label style={{ fontWeight: 'bold', fontSize: 14 }}>Contraseña</label>
          <input type="password" placeholder="Mínimo 8 caracteres" style={inputStyle} />
        </div>

        <button type="submit" style={buttonStyle}>
          Crear Cuenta
        </button>
      </form>

      <p style={{ textAlign: 'center', marginTop: 24, color: '#666' }}>
        ¿Ya tienes cuenta?{' '}
        <a href="/login" style={{ color: '#2E7D32' }}>Inicia sesión</a>
      </p>
    </div>
  );
}

const inputStyle = {
  width: '100%',
  padding: 12,
  border: '1px solid #ddd',
  borderRadius: 8,
  fontSize: 16,
  marginTop: 4,
  boxSizing: 'border-box',
};

const buttonStyle = {
  padding: 14,
  backgroundColor: '#2E7D32',
  color: '#fff',
  border: 'none',
  borderRadius: 8,
  fontSize: 16,
  fontWeight: 'bold',
  cursor: 'pointer',
  marginTop: 8,
};
