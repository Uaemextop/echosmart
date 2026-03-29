<?php
/**
 * EchoSmart — Front Page Template
 *
 * Landing page for echosmart.me with product information,
 * features, and call-to-action sections.
 *
 * @package EchoSmart
 */

get_header();
?>

<!-- Hero Section -->
<section class="es-hero">
    <div class="es-container es-hero__content">
        <h1><?php esc_html_e( 'Monitoreo Ambiental Inteligente para Invernaderos', 'echosmart' ); ?></h1>
        <p><?php esc_html_e( 'EchoSmart es la plataforma IoT que transforma la gestión de tu invernadero con sensores inteligentes, alertas en tiempo real y análisis predictivo.', 'echosmart' ); ?></p>
        <div class="es-hero__actions">
            <a href="<?php echo esc_url( home_url( '/dashboard' ) ); ?>" class="es-btn es-btn--accent">
                <?php esc_html_e( 'Comenzar Ahora', 'echosmart' ); ?>
            </a>
            <a href="<?php echo esc_url( home_url( '/features' ) ); ?>" class="es-btn es-btn--secondary" style="color:#fff;border-color:#fff;">
                <?php esc_html_e( 'Ver Características', 'echosmart' ); ?>
            </a>
        </div>
    </div>
</section>

<!-- Features Section -->
<section class="es-features">
    <div class="es-container">
        <div style="text-align:center;margin-bottom:var(--es-spacing-2xl);">
            <h2><?php esc_html_e( 'Todo lo que necesitas para tu invernadero', 'echosmart' ); ?></h2>
            <p style="color:var(--es-text-light);max-width:600px;margin:var(--es-spacing-md) auto 0;">
                <?php esc_html_e( 'Sensores de precisión, conectividad inteligente y análisis avanzado en una sola plataforma.', 'echosmart' ); ?>
            </p>
        </div>

        <div class="es-features__grid">
            <!-- Feature 1: Sensores -->
            <div class="es-feature-card">
                <div class="es-feature-card__icon">🌡️</div>
                <h3><?php esc_html_e( 'Sensores de Precisión', 'echosmart' ); ?></h3>
                <p><?php esc_html_e( 'Monitorea temperatura, humedad, luz y CO₂ con sensores de grado agrícola (DS18B20, DHT22, BH1750, MHZ-19C).', 'echosmart' ); ?></p>
            </div>

            <!-- Feature 2: Tiempo Real -->
            <div class="es-feature-card">
                <div class="es-feature-card__icon">📊</div>
                <h3><?php esc_html_e( 'Datos en Tiempo Real', 'echosmart' ); ?></h3>
                <p><?php esc_html_e( 'Visualiza las condiciones de tu invernadero en tiempo real con gráficas interactivas y dashboards personalizables.', 'echosmart' ); ?></p>
            </div>

            <!-- Feature 3: Alertas -->
            <div class="es-feature-card">
                <div class="es-feature-card__icon">🔔</div>
                <h3><?php esc_html_e( 'Alertas Inteligentes', 'echosmart' ); ?></h3>
                <p><?php esc_html_e( 'Recibe notificaciones push, email y SMS cuando los parámetros ambientales salen de los rangos óptimos.', 'echosmart' ); ?></p>
            </div>

            <!-- Feature 4: Gateway -->
            <div class="es-feature-card">
                <div class="es-feature-card__icon">📡</div>
                <h3><?php esc_html_e( 'Gateway EchoPy', 'echosmart' ); ?></h3>
                <p><?php esc_html_e( 'Hardware dedicado basado en Raspberry Pi con conectividad WiFi, Bluetooth y procesamiento edge.', 'echosmart' ); ?></p>
            </div>

            <!-- Feature 5: Reportes -->
            <div class="es-feature-card">
                <div class="es-feature-card__icon">📈</div>
                <h3><?php esc_html_e( 'Reportes y Análisis', 'echosmart' ); ?></h3>
                <p><?php esc_html_e( 'Genera reportes históricos, identifica tendencias y optimiza las condiciones de cultivo con análisis predictivo.', 'echosmart' ); ?></p>
            </div>

            <!-- Feature 6: Mobile -->
            <div class="es-feature-card">
                <div class="es-feature-card__icon">📱</div>
                <h3><?php esc_html_e( 'App Móvil', 'echosmart' ); ?></h3>
                <p><?php esc_html_e( 'Controla todo desde tu celular con nuestra app nativa para iOS y Android con notificaciones push.', 'echosmart' ); ?></p>
            </div>
        </div>
    </div>
</section>

<!-- Stats Section -->
<section class="es-stats">
    <div class="es-container">
        <div class="es-stats__grid">
            <div>
                <span class="es-stat__number">5</span>
                <span class="es-stat__label"><?php esc_html_e( 'Tipos de Sensores', 'echosmart' ); ?></span>
            </div>
            <div>
                <span class="es-stat__number">24/7</span>
                <span class="es-stat__label"><?php esc_html_e( 'Monitoreo Continuo', 'echosmart' ); ?></span>
            </div>
            <div>
                <span class="es-stat__number">&lt;1s</span>
                <span class="es-stat__label"><?php esc_html_e( 'Latencia de Datos', 'echosmart' ); ?></span>
            </div>
            <div>
                <span class="es-stat__number">99.9%</span>
                <span class="es-stat__label"><?php esc_html_e( 'Disponibilidad', 'echosmart' ); ?></span>
            </div>
        </div>
    </div>
</section>

<!-- CTA Section -->
<section class="es-cta">
    <div class="es-container">
        <h2><?php esc_html_e( '¿Listo para optimizar tu invernadero?', 'echosmart' ); ?></h2>
        <p><?php esc_html_e( 'Adquiere tu kit EchoPy y comienza a monitorear tu invernadero hoy mismo.', 'echosmart' ); ?></p>
        <a href="<?php echo esc_url( home_url( '/contact' ) ); ?>" class="es-btn es-btn--primary">
            <?php esc_html_e( 'Solicitar Información', 'echosmart' ); ?>
        </a>
    </div>
</section>

<?php
get_footer();
