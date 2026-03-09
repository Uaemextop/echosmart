# EchoSmart - Documentación de Frontend (React.js)

## 1. Estructura de Componentes React

### 1.1 Componentes por Feature

```
frontend/src/components/
├── Dashboard/
│   ├── DashboardLayout.jsx        # Layout principal con sidebar
│   ├── SensorCard.jsx              # Card individual de sensor
│   ├── SensorGrid.jsx              # Grilla responsiva de sensores
│   ├── QuickStats.jsx              # KPIs: Total sensores, Online, Alertas
│   └── DashboardSkeleton.jsx       # Loading state
│
├── Charts/
│   ├── TemperatureChart.jsx        # Gráfica de línea temporal
│   ├── HumidityChart.jsx           # Gráfica de humedad
│   ├── ComparisonChart.jsx         # Múltiples sensores overlay
│   ├── HeatmapChart.jsx            # Distribución espacial
│   └── ChartTooltip.jsx            # Tooltip personalizado
│
├── Sensors/
│   ├── SensorList.jsx              # Tabla de sensores (CRUD)
│   ├── SensorModal.jsx             # Modal crear/editar sensor
│   ├── SensorDetailPanel.jsx       # Panel lateral con detalles
│   ├── SensorStatusIndicator.jsx   # Badge online/offline
│   └── SensorFormFields.jsx        # Form fields reutilizables
│
├── Alerts/
│   ├── AlertCenter.jsx             # Centro de notificaciones
│   ├── AlertRule.jsx               # Crear/editar regla de alerta
│   ├── AlertHistory.jsx            # Historial de alertas
│   ├── AlertBanner.jsx             # Banner de alerta crítica
│   └── AlertModal.jsx              # Modal para acknowledgment
│
├── Reports/
│   ├── ReportGenerator.jsx         # Wizard para generar reportes
│   ├── ReportList.jsx              # Lista de reportes guardados
│   ├── ReportPreview.jsx           # Preview de reporte
│   └── ReportStatusBadge.jsx       # Estado del reporte (generating, ready)
│
├── Admin/
│   ├── AdminPanel.jsx              # Contenedor principal admin
│   ├── UserManagement.jsx          # CRUD usuarios
│   ├── TenantSettings.jsx          # Configurar tenant
│   ├── GatewayManager.jsx          # Gestionar gateways
│   ├── BrandingSettings.jsx        # Logo, colores, empresa
│   └── AuditLog.jsx                # Log de auditoría
│
├── Auth/
│   ├── LoginForm.jsx               # Formulario login
│   ├── ForgotPassword.jsx          # Reset password
│   ├── ProtectedRoute.jsx          # HOC para rutas privadas
│   └── AuthContext.jsx             # Context de autenticación
│
├── Common/
│   ├── Header.jsx                  # Navbar principal
│   ├── Sidebar.jsx                 # Menu lateral
│   ├── Footer.jsx                  # Pie de página
│   ├── Breadcrumb.jsx              # Navegación breadcrumb
│   ├── Pagination.jsx              # Control de paginación
│   ├── LoadingSpinner.jsx          # Spinner de carga
│   ├── ErrorBoundary.jsx           # Boundary para errores
│   ├── ConfirmDialog.jsx           # Diálogo de confirmación
│   ├── Toast.jsx                   # Notificaciones toast
│   └── Badge.jsx                   # Badges reutilizables
│
└── Forms/
    ├── FormInput.jsx               # Input con validación
    ├── FormSelect.jsx              # Select component
    ├── FormDateRange.jsx           # Selector de rango de fechas
    ├── FormCheckbox.jsx            # Checkbox
    └── FormSubmit.jsx              # Botón submit con loading
```

---

### 1.2 Hook Personalizado: `useReadings`

```javascript
// src/hooks/useReadings.js

/**
 * Hook para fetching y caching de lecturas de sensores
 * 
 * Responsabilidades:
 *  • Fetch datos desde API REST
 *  • Caché local en Redux
 *  • Auto-refresh periódico
 *  • Manejo de errores y retry
 */

function useReadings(sensorId, { from, to, interval = 300 }) {
  const dispatch = useDispatch();
  const readings = useSelector(state => state.readings.data[sensorId] || []);
  const loading = useSelector(state => state.readings.loading);
  const error = useSelector(state => state.readings.error);
  
  useEffect(() => {
    if (!sensorId) return;
    
    // Fetch inicial
    const fetchReadings = async () => {
      try {
        dispatch({ type: 'READINGS_LOADING' });
        
        const response = await fetch(
          `/api/v1/readings/${sensorId}?from=${from}&to=${to}&interval=${interval}`,
          {
            headers: {
              'Authorization': `Bearer ${getAuthToken()}`
            }
          }
        );
        
        if (!response.ok) throw new Error('Failed to fetch readings');
        
        const data = await response.json();
        
        dispatch({
          type: 'READINGS_SUCCESS',
          payload: { sensorId, readings: data.data }
        });
      } catch (err) {
        dispatch({ type: 'READINGS_ERROR', payload: err.message });
        
        // Retry después de 3 segundos (exponential backoff)
        setTimeout(fetchReadings, 3000);
      }
    };
    
    fetchReadings();
    
    // Auto-refresh cada 60 segundos
    const interval = setInterval(fetchReadings, 60000);
    
    return () => clearInterval(interval);
  }, [sensorId, from, to, dispatch]);
  
  return { readings, loading, error };
}
```

---

### 1.3 Custom Hook: `useWebSocket`

```javascript
// src/hooks/useWebSocket.js

/**
 * Hook para conexión WebSocket a actualizaciones en tiempo real
 * 
 * Responsabilidades:
 *  • Conectar al servidor WebSocket
 *  • Subscribirse a sensores específicos
 *  • Recibir updates en tiempo real
 *  • Manejar reconexión automática
 *  • Actualizar Redux store
 */

function useWebSocket(sensorIds = []) {
  const dispatch = useDispatch();
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {
    if (!sensorIds.length) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(
      `${protocol}//${window.location.host}/ws/sensors?token=${getAuthToken()}`
    );
    
    ws.onopen = () => {
      setConnected(true);
      
      // Subscribirse a cada sensor
      sensorIds.forEach(id => {
        ws.send(JSON.stringify({
          type: 'subscribe',
          sensor_id: id
        }));
      });
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      // Despachar a Redux
      dispatch({
        type: 'SENSOR_UPDATE_RECEIVED',
        payload: {
          sensor_id: message.sensor_id,
          reading: message.reading,
          timestamp: message.timestamp
        }
      });
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
    
    ws.onclose = () => {
      setConnected(false);
      
      // Reconectar después de 5 segundos
      setTimeout(() => {
        // Trigger re-render para reconectar
      }, 5000);
    };
    
    return () => ws.close();
  }, [sensorIds, dispatch]);
  
  return { connected };
}
```

---

### 1.4 Redux Slices

```javascript
// src/store/slices/sensorsSlice.js

const sensorsSlice = createSlice({
  name: 'sensors',
  initialState: {
    byId: {},           // {sensor_id: {...}}
    allIds: [],         // [sensor_id1, sensor_id2, ...]
    loading: false,
    error: null,
    filters: {
      gatewayId: null,
      type: null,
      search: ''
    }
  },
  
  reducers: {
    sensorsLoading: (state) => {
      state.loading = true;
      state.error = null;
    },
    
    sensorsLoaded: (state, action) => {
      state.loading = false;
      
      // Normalizar sensores
      action.payload.forEach(sensor => {
        state.byId[sensor.id] = sensor;
        if (!state.allIds.includes(sensor.id)) {
          state.allIds.push(sensor.id);
        }
      });
    },
    
    sensorUpdated: (state, action) => {
      const { id, ...updates } = action.payload;
      state.byId[id] = { ...state.byId[id], ...updates };
    },
    
    sensorDeleted: (state, action) => {
      delete state.byId[action.payload];
      state.allIds = state.allIds.filter(id => id !== action.payload);
    },
    
    setFilters: (state, action) => {
      state.filters = action.payload;
    }
  }
});

// Selectores
export const selectSensorById = (state, sensorId) => 
  state.sensors.byId[sensorId];

export const selectVisibleSensors = (state) => {
  const { sensors, filters } = state.sensors;
  
  return sensors.allIds
    .map(id => sensors.byId[id])
    .filter(sensor => {
      if (filters.gatewayId && sensor.gateway_id !== filters.gatewayId) 
        return false;
      if (filters.type && sensor.type !== filters.type) 
        return false;
      if (filters.search && 
          !sensor.name.toLowerCase().includes(filters.search.toLowerCase())) 
        return false;
      return true;
    });
};
```

---

## 2. Estados y Flujos de UI

### 2.1 Dashboard State Machine

```javascript
// Estados posibles del dashboard
const DashboardStates = {
  // Initial
  LOADING: 'loading',           // Cargando datos iniciales
  
  // Success
  READY: 'ready',               // Datos cargados, mostrando dashboard
  
  // Partial
  STALE: 'stale',               // Datos un poco desactualizados
  
  // Errors
  SENSOR_ERROR: 'sensor_error', // No se pudieron cargar sensores
  NO_DATA: 'no_data',           // Tenant sin sensores aún
  NETWORK_ERROR: 'network_error' // Error de red
};

// Transiciones
const transitions = {
  LOADING: {
    success: READY,
    error_sensors: SENSOR_ERROR,
    error_network: NETWORK_ERROR,
    empty: NO_DATA
  },
  READY: {
    stale_data: STALE,
    new_alert: READY,  // No cambiar estado
    error: NETWORK_ERROR
  },
  // etc...
};
```

### 2.2 Componente Dashboard

```javascript
// src/pages/Dashboard.jsx

function Dashboard() {
  const dispatch = useDispatch();
  const { sensors, loading, error } = useSelector(state => state.sensors);
  const { alerts } = useSelector(state => state.alerts);
  const [state, setState] = useState('loading');
  
  useEffect(() => {
    // Cargar sensores al montar
    dispatch(fetchSensors())
      .then(() => setState('ready'))
      .catch(() => setState('error'));
  }, [dispatch]);
  
  if (state === 'loading') {
    return <DashboardSkeleton />;
  }
  
  if (sensors.length === 0) {
    return <EmptyState />;
  }
  
  return (
    <DashboardLayout>
      <QuickStats alerts={alerts} sensorsCount={sensors.length} />
      
      <div className="grid grid-cols-3 gap-4">
        {sensors.map(sensor => (
          <SensorCard 
            key={sensor.id} 
            sensor={sensor}
            onSelect={() => showSensorDetail(sensor.id)}
          />
        ))}
      </div>
      
      {alerts.length > 0 && (
        <AlertBanner alerts={alerts} />
      )}
    </DashboardLayout>
  );
}
```

---

## 3. Gestión de Estado Global (Redux)

### 3.1 Estructura de Redux Store

```javascript
// src/store/store.js

export const store = configureStore({
  reducer: {
    auth: authSlice,        // { user, token, isAuthenticated }
    sensors: sensorsSlice,  // { byId, allIds, loading, filters }
    readings: readingsSlice, // { data, loading, error }
    alerts: alertsSlice,    // { active, history, loading }
    reports: reportsSlice,  // { list, generating, error }
    ui: uiSlice,            // { theme, sidebar, notifications }
    admin: adminSlice       // { users, tenants, settings }
  },
  
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['HYDRATE'],
        ignoredPaths: ['auth.token']  // Token no es serializable
      }
    })
    .concat(customMiddleware)
});
```

---

## 4. Internacionalización (i18n)

```javascript
// src/i18n/es.json
{
  "dashboard": {
    "title": "Dashboard",
    "sensors_online": "Sensores en línea",
    "active_alerts": "Alertas activas"
  },
  "sensors": {
    "name": "Nombre",
    "type": "Tipo",
    "location": "Ubicación",
    "status": "Estado"
  },
  "alerts": {
    "critical": "Crítica",
    "high": "Alta",
    "medium": "Media",
    "low": "Baja"
  }
}

// Uso:
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  return <h1>{t('dashboard.title')}</h1>;
}
```

---

## 5. Theming (Personalización por Tenant)

```javascript
// src/theme/tenantTheme.js

/**
 * Carga tema dinámico basado en configuración del tenant
 */

function useTenatTheme(tenant) {
  return {
    colors: {
      primary: tenant.branding?.primary_color || '#1E3A8A',
      secondary: tenant.branding?.secondary_color || '#2D5A3D',
      background: '#ffffff',
      text: '#0f172a'
    },
    logo: tenant.branding?.logo_url,
    company_name: tenant.branding?.company_name_display
  };
}

// Uso en CSS-in-JS (Emotion/Styled Components)
const StyledHeader = styled.header`
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.background};
`;
```

---

## 6. Testing en Frontend

### 6.1 Unit Tests (Jest + React Testing Library)

```javascript
// src/components/SensorCard.test.js

import { render, screen } from '@testing-library/react';
import { SensorCard } from './SensorCard';

describe('SensorCard', () => {
  const mockSensor = {
    id: 'sensor-1',
    name: 'Sensor Temperatura A',
    type: 'temperature',
    last_reading: { value: 25.3, unit: '°C' },
    is_online: true
  };
  
  it('should render sensor name', () => {
    render(<SensorCard sensor={mockSensor} />);
    expect(screen.getByText('Sensor Temperatura A')).toBeInTheDocument();
  });
  
  it('should display last reading', () => {
    render(<SensorCard sensor={mockSensor} />);
    expect(screen.getByText('25.3°C')).toBeInTheDocument();
  });
  
  it('should show online status', () => {
    render(<SensorCard sensor={mockSensor} />);
    expect(screen.getByTestId('status-badge')).toHaveClass('online');
  });
  
  it('should handle click to view details', () => {
    const handleClick = jest.fn();
    render(<SensorCard sensor={mockSensor} onSelect={handleClick} />);
    
    screen.getByRole('button').click();
    expect(handleClick).toHaveBeenCalledWith(mockSensor);
  });
});
```

---

## 7. Performance Optimization

### 7.1 Code Splitting

```javascript
// src/App.jsx

import { Suspense, lazy } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const AdminPanel = lazy(() => import('./pages/AdminPanel'));
const Reports = lazy(() => import('./pages/Reports'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </Suspense>
  );
}
```

### 7.2 Memoización

```javascript
// Evitar re-renders innecesarios

const SensorCard = React.memo(
  ({ sensor, onSelect }) => (
    <div onClick={() => onSelect(sensor)}>
      {sensor.name}: {sensor.last_reading.value}
    </div>
  ),
  (prevProps, nextProps) => {
    // Custom comparison
    return (
      prevProps.sensor.id === nextProps.sensor.id &&
      prevProps.sensor.last_reading === nextProps.sensor.last_reading
    );
  }
);
```

### 7.3 Virtualización de Listas

```javascript
// Para listas >100 items, usar react-window

import { FixedSizeList } from 'react-window';

function SensorList({ sensors }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={sensors.length}
      itemSize={35}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          <SensorRow sensor={sensors[index]} />
        </div>
      )}
    </FixedSizeList>
  );
}
```

