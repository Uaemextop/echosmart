-- RLS Policies using app.current_tenant_id session variable set by backend

-- tenant_settings policies
CREATE POLICY tenant_settings_isolation ON tenant_settings
  USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);

-- users policies
CREATE POLICY users_tenant_isolation ON users
  USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID
    OR role = 'superadmin');

-- sensors policies
CREATE POLICY sensors_tenant_isolation ON sensors
  USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);

-- alert_rules policies
CREATE POLICY alert_rules_tenant_isolation ON alert_rules
  USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);

-- alert_history policies
CREATE POLICY alert_history_tenant_isolation ON alert_history
  USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);

-- notification_channels policies
CREATE POLICY notification_channels_tenant_isolation ON notification_channels
  USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::UUID);
