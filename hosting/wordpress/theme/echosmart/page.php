<?php
/**
 * EchoSmart — Default Page Template
 *
 * @package EchoSmart
 */

get_header();
?>

<main class="es-container" style="padding: var(--es-spacing-2xl) var(--es-spacing-lg);">
    <?php
    while ( have_posts() ) :
        the_post();
    ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <h1><?php the_title(); ?></h1>
            <div class="entry-content">
                <?php the_content(); ?>
            </div>
        </article>
    <?php endwhile; ?>
</main>

<?php
get_footer();
