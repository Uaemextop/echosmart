<?php
/**
 * EchoSmart WordPress Theme — Functions
 *
 * @package EchoSmart
 * @version 1.0.0
 */

defined( 'ABSPATH' ) || exit;

// ---- Constants ----
define( 'ECHOSMART_THEME_VERSION', '1.0.0' );
define( 'ECHOSMART_THEME_DIR', get_template_directory() );
define( 'ECHOSMART_THEME_URI', get_template_directory_uri() );

/**
 * Theme setup — runs after theme is loaded.
 */
function echosmart_setup() {
    // Add theme support
    add_theme_support( 'title-tag' );
    add_theme_support( 'post-thumbnails' );
    add_theme_support( 'custom-logo', array(
        'height'      => 80,
        'width'       => 200,
        'flex-height' => true,
        'flex-width'  => true,
    ) );
    add_theme_support( 'html5', array(
        'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script',
    ) );
    add_theme_support( 'responsive-embeds' );

    // Register navigation menus
    register_nav_menus( array(
        'primary'  => __( 'Menú Principal', 'echosmart' ),
        'footer'   => __( 'Menú Footer', 'echosmart' ),
    ) );

    // Load text domain for translations
    load_theme_textdomain( 'echosmart', ECHOSMART_THEME_DIR . '/languages' );
}
add_action( 'after_setup_theme', 'echosmart_setup' );

/**
 * Enqueue theme styles and scripts.
 */
function echosmart_enqueue_assets() {
    // Google Fonts — Inter
    wp_enqueue_style(
        'echosmart-fonts',
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
        array(),
        null
    );

    // Theme stylesheet
    wp_enqueue_style(
        'echosmart-style',
        get_stylesheet_uri(),
        array( 'echosmart-fonts' ),
        ECHOSMART_THEME_VERSION
    );

    // Theme JavaScript
    wp_enqueue_script(
        'echosmart-main',
        ECHOSMART_THEME_URI . '/assets/js/main.js',
        array(),
        ECHOSMART_THEME_VERSION,
        true
    );

    // Pass configuration to JavaScript
    wp_localize_script( 'echosmart-main', 'echosmartConfig', array(
        'apiUrl'     => defined( 'ECHOSMART_API_URL' ) ? ECHOSMART_API_URL : '',
        'apiVersion' => defined( 'ECHOSMART_API_VERSION' ) ? ECHOSMART_API_VERSION : 'v1',
        'siteUrl'    => home_url(),
        'themeUrl'   => ECHOSMART_THEME_URI,
        'nonce'      => wp_create_nonce( 'echosmart_nonce' ),
    ) );
}
add_action( 'wp_enqueue_scripts', 'echosmart_enqueue_assets' );

/**
 * Register widget areas.
 */
function echosmart_widgets_init() {
    register_sidebar( array(
        'name'          => __( 'Footer Widget Area', 'echosmart' ),
        'id'            => 'footer-widgets',
        'description'   => __( 'Widgets en el footer del sitio.', 'echosmart' ),
        'before_widget' => '<div class="es-footer__widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h4>',
        'after_title'   => '</h4>',
    ) );
}
add_action( 'widgets_init', 'echosmart_widgets_init' );

/**
 * Custom page template for the EchoSmart dashboard (React SPA).
 */
function echosmart_dashboard_template( $template ) {
    if ( is_page( 'dashboard' ) || is_page( 'app' ) ) {
        $custom = ECHOSMART_THEME_DIR . '/page-dashboard.php';
        if ( file_exists( $custom ) ) {
            return $custom;
        }
    }
    return $template;
}
add_filter( 'template_include', 'echosmart_dashboard_template' );

/**
 * Add custom body classes.
 */
function echosmart_body_classes( $classes ) {
    $classes[] = 'echosmart-theme';

    if ( is_front_page() ) {
        $classes[] = 'echosmart-home';
    }

    if ( is_page( 'dashboard' ) || is_page( 'app' ) ) {
        $classes[] = 'echosmart-dashboard';
    }

    return $classes;
}
add_filter( 'body_class', 'echosmart_body_classes' );

/**
 * Customize the login page to match EchoSmart branding.
 */
function echosmart_login_styles() {
    ?>
    <style>
        body.login {
            background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #00BCD4 100%);
        }
        .login h1 a {
            background-image: none !important;
            font-size: 2rem;
            font-weight: 800;
            color: #fff;
            width: auto;
            height: auto;
            text-indent: 0;
        }
        .login h1 a::after {
            content: 'EchoSmart';
        }
        .login form {
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }
        .login #backtoblog a,
        .login #nav a {
            color: rgba(255,255,255,0.8) !important;
        }
        .login #backtoblog a:hover,
        .login #nav a:hover {
            color: #fff !important;
        }
        .wp-core-ui .button-primary {
            background: #2E7D32 !important;
            border-color: #1B5E20 !important;
        }
        .wp-core-ui .button-primary:hover {
            background: #1B5E20 !important;
        }
    </style>
    <?php
}
add_action( 'login_enqueue_scripts', 'echosmart_login_styles' );

/**
 * Change login logo URL.
 */
function echosmart_login_url() {
    return home_url();
}
add_filter( 'login_headerurl', 'echosmart_login_url' );

/**
 * Remove WordPress version from head for security.
 */
remove_action( 'wp_head', 'wp_generator' );

/**
 * Disable XML-RPC for security.
 */
add_filter( 'xmlrpc_enabled', '__return_false' );

/**
 * Register custom EchoSmart shortcodes.
 */
function echosmart_dashboard_shortcode( $atts ) {
    $atts = shortcode_atts( array(
        'height' => '80vh',
    ), $atts, 'echosmart_dashboard' );

    $api_url = defined( 'ECHOSMART_API_URL' ) ? ECHOSMART_API_URL : '';

    return sprintf(
        '<div id="echosmart-app" class="es-app-container" data-api="%s" style="min-height:%s;"></div>',
        esc_attr( $api_url ),
        esc_attr( $atts['height'] )
    );
}
add_shortcode( 'echosmart_dashboard', 'echosmart_dashboard_shortcode' );

/**
 * Add EchoSmart admin menu for WordPress.
 */
function echosmart_admin_menu() {
    add_menu_page(
        __( 'EchoSmart', 'echosmart' ),
        __( 'EchoSmart', 'echosmart' ),
        'manage_options',
        'echosmart-settings',
        'echosmart_settings_page',
        'dashicons-chart-area',
        30
    );
}
add_action( 'admin_menu', 'echosmart_admin_menu' );

/**
 * EchoSmart settings page in wp-admin.
 */
function echosmart_settings_page() {
    if ( ! current_user_can( 'manage_options' ) ) {
        return;
    }

    // Save settings
    if ( isset( $_POST['echosmart_save'] ) && check_admin_referer( 'echosmart_settings' ) ) {
        update_option( 'echosmart_api_url', sanitize_url( $_POST['echosmart_api_url'] ?? '' ) );
        update_option( 'echosmart_api_key', sanitize_text_field( $_POST['echosmart_api_key'] ?? '' ) );
        echo '<div class="notice notice-success"><p>' . esc_html__( 'Configuración guardada.', 'echosmart' ) . '</p></div>';
    }

    $api_url = get_option( 'echosmart_api_url', defined( 'ECHOSMART_API_URL' ) ? ECHOSMART_API_URL : '' );
    $api_key = get_option( 'echosmart_api_key', '' );
    ?>
    <div class="wrap">
        <h1><?php esc_html_e( 'EchoSmart — Configuración', 'echosmart' ); ?></h1>
        <form method="post">
            <?php wp_nonce_field( 'echosmart_settings' ); ?>
            <table class="form-table">
                <tr>
                    <th><label for="echosmart_api_url"><?php esc_html_e( 'API URL', 'echosmart' ); ?></label></th>
                    <td>
                        <input type="url" id="echosmart_api_url" name="echosmart_api_url"
                               value="<?php echo esc_attr( $api_url ); ?>" class="regular-text"
                               placeholder="https://api.echosmart.me" />
                        <p class="description"><?php esc_html_e( 'URL del backend de EchoSmart.', 'echosmart' ); ?></p>
                    </td>
                </tr>
                <tr>
                    <th><label for="echosmart_api_key"><?php esc_html_e( 'API Key', 'echosmart' ); ?></label></th>
                    <td>
                        <input type="password" id="echosmart_api_key" name="echosmart_api_key"
                               value="<?php echo esc_attr( $api_key ); ?>" class="regular-text" />
                        <p class="description"><?php esc_html_e( 'Clave de autenticación para la API.', 'echosmart' ); ?></p>
                    </td>
                </tr>
            </table>
            <p class="submit">
                <input type="submit" name="echosmart_save" class="button-primary"
                       value="<?php esc_attr_e( 'Guardar Configuración', 'echosmart' ); ?>" />
            </p>
        </form>
    </div>
    <?php
}
