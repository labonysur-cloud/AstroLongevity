/**
 * Move focus to the new page heading on Gravity Forms AJAX page change.
 *
 * Gravity Forms re-renders the form HTML via AJAX when the user clicks Next
 * or Previous on a multi-page form. By default, focus stays where it was
 * and screen readers receive no audible cue that the page has changed.
 *
 * This script listens for gform_post_render and moves focus to the active
 * page's heading after the swap, so the new content gets announced by
 * assistive technology. Initial render and same-page re-renders (validation
 * errors) are skipped so we don't disrupt natural reading flow or fight
 * Gravity Forms' field-level focus on validation.
 */
( function ( $ ) {
	'use strict';

	if ( ! $ ) {
		return;
	}

	var lastPageByForm = {};

	$( document ).on( 'gform_post_render', function ( event, formId, currentPage ) {

		// Skip the initial render — only move focus on actual page change.
		if ( typeof lastPageByForm[ formId ] === 'undefined' ) {
			lastPageByForm[ formId ] = currentPage;
			return;
		}

		// Same page (e.g., validation error re-render) — let Gravity Forms
		// focus the first invalid field instead.
		if ( lastPageByForm[ formId ] === currentPage ) {
			return;
		}

		lastPageByForm[ formId ] = currentPage;

		var $form   = $( '#gform_' + formId );
		var $active = $form.find( '.gform_page' ).filter( function () {
			return $( this ).css( 'display' ) !== 'none';
		} ).first();

		// Prefer the active page's first heading; fall back to the HDS
		// stepper, then to the form wrapper itself.
		var $target = $active.find( 'h2, h3, h4, h5, h6' ).first();
		if ( ! $target.length ) {
			$target = $form.find( '.hds-gf-stepper' ).first();
		}
		if ( ! $target.length ) {
			$target = $form;
		}

		if ( ! $target.attr( 'tabindex' ) ) {
			$target.attr( 'tabindex', '-1' );
		}
		$target.trigger( 'focus' );
	} );
} )( window.jQuery );
