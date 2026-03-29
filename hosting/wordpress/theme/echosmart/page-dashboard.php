<?php
/**
 * EchoSmart — Dashboard Page Template
 *
 * Template Name: EchoSmart Dashboard
 *
 * Renders the React SPA application for the IoT dashboard.
 * The frontend app is deployed to the /app/ subdirectory
 * within the theme.
 *
 * @package EchoSmart
 */

get_header();

$api_url     = get_option( 'echosmart_api_url', defined( 'ECHOSMART_API_URL' ) ? ECHOSMART_API_URL : '' );
$api_version = defined( 'ECHOSMART_API_VERSION' ) ? ECHOSMART_API_VERSION : 'v1';
$app_dir     = ECHOSMART_THEME_URI . '/app/';
?>

<main class="es-app-container">
    <div id="echosmart-app"
         data-api="<?php echo esc_attr( $api_url ); ?>"
         data-api-version="<?php echo esc_attr( $api_version ); ?>"
         style="min-height: 80vh; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center; color: var(--es-text-light);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⏳</div>
            <p><?php esc_html_e( 'Cargando EchoSmart Dashboard...', 'echosmart' ); ?></p>
        </div>
    </div>
</main>

<?php
// Load the React SPA assets if they exist
$app_index = ECHOSMART_THEME_DIR . '/app/index.html';
if ( file_exists( $app_index ) ) {
    // Parse the built index.html to extract JS/CSS references
    $html = file_get_contents( $app_index );

    // Extract and enqueue CSS files
    if ( preg_match_all( '/href="([^"]*\.css)"/', $html, $css_matches ) ) {
        foreach ( $css_matches[1] as $i => $css_file ) {
            $css_url = $app_dir . ltrim( $css_file, './' );
            wp_enqueue_style( "echosmart-app-css-{$i}", $css_url, array(), ECHOSMART_THEME_VERSION );
        }
    }

    // Extract and enqueue JS files
    if ( preg_match_all( '/src="([^"]*\.js)"/', $html, $js_matches ) ) {
        foreach ( $js_matches[1] as $i => $js_file ) {
            $js_url = $app_dir . ltrim( $js_file, './' );
            wp_enqueue_script(
                "echosmart-app-js-{$i}",
                $js_url,
                array(),
                ECHOSMART_THEME_VERSION,
                true
            );
        }
    }
}

get_footer();
