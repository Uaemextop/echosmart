<!-- Footer -->
<footer class="es-footer">
    <div class="es-container">
        <div class="es-footer__grid">
            <div>
                <h4>EchoSmart</h4>
                <p>Plataforma IoT de monitoreo ambiental inteligente para invernaderos.</p>
            </div>
            <div>
                <h4><?php esc_html_e( 'Producto', 'echosmart' ); ?></h4>
                <a href="<?php echo esc_url( home_url( '/features' ) ); ?>"><?php esc_html_e( 'Características', 'echosmart' ); ?></a>
                <a href="<?php echo esc_url( home_url( '/pricing' ) ); ?>"><?php esc_html_e( 'Precios', 'echosmart' ); ?></a>
                <a href="<?php echo esc_url( home_url( '/docs' ) ); ?>"><?php esc_html_e( 'Documentación', 'echosmart' ); ?></a>
            </div>
            <div>
                <h4><?php esc_html_e( 'Soporte', 'echosmart' ); ?></h4>
                <a href="<?php echo esc_url( home_url( '/contact' ) ); ?>"><?php esc_html_e( 'Contacto', 'echosmart' ); ?></a>
                <a href="<?php echo esc_url( home_url( '/faq' ) ); ?>"><?php esc_html_e( 'FAQ', 'echosmart' ); ?></a>
                <a href="<?php echo esc_url( home_url( '/status' ) ); ?>"><?php esc_html_e( 'Estado del Sistema', 'echosmart' ); ?></a>
            </div>
            <div>
                <h4><?php esc_html_e( 'Legal', 'echosmart' ); ?></h4>
                <a href="<?php echo esc_url( home_url( '/privacy' ) ); ?>"><?php esc_html_e( 'Privacidad', 'echosmart' ); ?></a>
                <a href="<?php echo esc_url( home_url( '/terms' ) ); ?>"><?php esc_html_e( 'Términos', 'echosmart' ); ?></a>
            </div>
        </div>
        <div class="es-footer__bottom">
            <p>&copy; <?php echo esc_html( date( 'Y' ) ); ?> EchoSmart. <?php esc_html_e( 'Todos los derechos reservados.', 'echosmart' ); ?></p>
        </div>
    </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
