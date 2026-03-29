<?php
/**
 * EchoSmart — Default Template (index.php)
 *
 * @package EchoSmart
 */

get_header();
?>

<main class="es-container" style="padding: var(--es-spacing-2xl) var(--es-spacing-lg);">
    <?php if ( have_posts() ) : ?>
        <?php while ( have_posts() ) : the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?> style="margin-bottom: var(--es-spacing-xl);">
                <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
                <div class="entry-content">
                    <?php the_excerpt(); ?>
                </div>
            </article>
        <?php endwhile; ?>

        <?php the_posts_pagination(); ?>
    <?php else : ?>
        <p><?php esc_html_e( 'No se encontraron publicaciones.', 'echosmart' ); ?></p>
    <?php endif; ?>
</main>

<?php
get_footer();
