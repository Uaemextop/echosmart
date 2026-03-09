export interface Tenant {
  id: string;
  name: string;
  plan: 'basic' | 'pro' | 'enterprise';
  status: 'active' | 'suspended' | 'deleted';
  maxSensors: number;
  maxUsers: number;
  createdAt: string;
  settings?: TenantSettings;
}

export interface TenantSettings {
  logoUrl: string;
  primaryColor: string;
  secondaryColor: string;
  companyName: string;
  emailSignatureHtml: string;
  timezone: string;
  language: string;
}

export interface User {
  id: string;
  tenantId: string | null;
  email: string;
  role: 'superadmin' | 'tenant_admin' | 'user';
  firstName?: string;
  lastName?: string;
  emailVerified: boolean;
}

export interface Sensor {
  id: string;
  tenantId: string;
  uuid: string;
  sensorType: string;
  capabilities: string[];
  status: 'online' | 'offline' | 'error';
  gatewayId: string;
  lastSeen: string | null;
  influxdbMeasurement: string;
}

export interface SensorReading {
  timestamp: string;
  temperature?: number;
  humidity?: number;
  co2?: number;
  light?: number;
  soilMoisture?: number;
}

export interface AlertRule {
  id: string;
  tenantId: string;
  sensorId: string;
  name: string;
  conditions: AlertCondition;
  hysteresisCount: number;
  timeWindowStart?: string;
  timeWindowEnd?: string;
  severity: 'info' | 'warning' | 'critical';
  isActive: boolean;
  notificationChannels: string[];
}

export interface AlertCondition {
  operator: 'AND' | 'OR' | 'NOT';
  conditions: Array<AlertConditionLeaf | AlertCondition>;
}

export interface AlertConditionLeaf {
  field: string;
  op: '>' | '<' | '>=' | '<=' | '==' | '!=';
  value: number;
}

export interface AlertHistory {
  id: string;
  alertRuleId: string;
  sensorId: string;
  triggeredAt: string;
  resolvedAt?: string;
  severity: string;
  message: string;
  acknowledged: boolean;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
}
