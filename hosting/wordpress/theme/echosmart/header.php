<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="<?php bloginfo( 'description' ); ?>">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- Header -->
<header class="es-header">
    <div class="es-container es-header__inner">
        <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="es-header__logo">
            <?php if ( has_custom_logo() ) : ?>
                <?php the_custom_logo(); ?>
            <?php else : ?>
                <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="20" cy="20" r="18" fill="#2E7D32" opacity="0.1"/>
                    <path d="M20 8C13.4 8 8 13.4 8 20s5.4 12 12 12 12-5.4 12-12S26.6 8 20 8zm-1 17.9V22h-3l5-9.9V18h3l-5 7.9z" fill="#2E7D32"/>
                </svg>
            <?php endif; ?>
            <span>EchoSmart</span>
        </a>

        <nav class="es-nav">
            <?php
            wp_nav_menu( array(
                'theme_location' => 'primary',
                'container'      => false,
                'items_wrap'     => '%3$s',
                'depth'          => 1,
                'fallback_cb'    => function() {
                    echo '<a href="' . esc_url( home_url( '/' ) ) . '">Inicio</a>';
                    echo '<a href="' . esc_url( home_url( '/features' ) ) . '">Características</a>';
                    echo '<a href="' . esc_url( home_url( '/pricing' ) ) . '">Precios</a>';
                    echo '<a href="' . esc_url( home_url( '/contact' ) ) . '">Contacto</a>';
                },
            ) );
            ?>
            <a href="<?php echo esc_url( home_url( '/dashboard' ) ); ?>" class="es-btn es-btn--primary">
                Acceder al Panel
            </a>
        </nav>
    </div>
</header>
