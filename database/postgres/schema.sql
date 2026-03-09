-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- tenants table
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL UNIQUE,
  plan VARCHAR(20) NOT NULL DEFAULT 'basic' CHECK (plan IN ('basic', 'pro', 'enterprise')),
  status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
  max_sensors INTEGER NOT NULL DEFAULT 10,
  max_users INTEGER NOT NULL DEFAULT 5,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- tenant_settings table
CREATE TABLE tenant_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  logo_url TEXT DEFAULT '',
  primary_color VARCHAR(7) DEFAULT '#22c55e',
  secondary_color VARCHAR(7) DEFAULT '#16a34a',
  company_name VARCHAR(200) DEFAULT '',
  email_signature_html TEXT DEFAULT '',
  timezone VARCHAR(50) DEFAULT 'UTC',
  language VARCHAR(10) DEFAULT 'en',
  notification_email VARCHAR(200),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(tenant_id)
);

-- users table with RBAC
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  email VARCHAR(200) NOT NULL UNIQUE,
  password_hash VARCHAR(200) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('superadmin', 'tenant_admin', 'user')),
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- refresh_tokens table
CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(200) NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  revoked BOOLEAN NOT NULL DEFAULT FALSE
);

-- sensors table
CREATE TABLE sensors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  uuid VARCHAR(100) NOT NULL UNIQUE,
  sensor_type VARCHAR(50) NOT NULL,
  capabilities JSONB DEFAULT '[]',
  status VARCHAR(20) NOT NULL DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'error')),
  gateway_id VARCHAR(100),
  ip_address VARCHAR(45),
  port INTEGER,
  influxdb_measurement VARCHAR(100),
  last_seen TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- alert_rules table with JSONB conditions
CREATE TABLE alert_rules (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  sensor_id UUID REFERENCES sensors(id) ON DELETE CASCADE,
  name VARCHAR(200) NOT NULL,
  conditions JSONB NOT NULL,
  hysteresis_count INTEGER NOT NULL DEFAULT 1,
  time_window_start TIME,
  time_window_end TIME,
  severity VARCHAR(20) NOT NULL DEFAULT 'warning' CHECK (severity IN ('info', 'warning', 'critical')),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  notification_channels JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- alert_history table
CREATE TABLE alert_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  alert_rule_id UUID REFERENCES alert_rules(id) ON DELETE SET NULL,
  sensor_id UUID REFERENCES sensors(id) ON DELETE SET NULL,
  triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ,
  severity VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  sensor_data JSONB,
  acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
  acknowledged_by UUID REFERENCES users(id)
);

-- notification_channels table
CREATE TABLE notification_channels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  channel_type VARCHAR(20) NOT NULL CHECK (channel_type IN ('email', 'whatsapp', 'webhook')),
  config JSONB NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_sensors_tenant_id ON sensors(tenant_id);
CREATE INDEX idx_sensors_uuid ON sensors(uuid);
CREATE INDEX idx_sensors_status ON sensors(status);
CREATE INDEX idx_alert_rules_tenant_id ON alert_rules(tenant_id);
CREATE INDEX idx_alert_rules_sensor_id ON alert_rules(sensor_id);
CREATE INDEX idx_alert_history_tenant_id ON alert_history(tenant_id);
CREATE INDEX idx_alert_history_triggered_at ON alert_history(triggered_at DESC);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);

-- Enable RLS on tenant-scoped tables
ALTER TABLE tenant_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensors ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_channels ENABLE ROW LEVEL SECURITY;
