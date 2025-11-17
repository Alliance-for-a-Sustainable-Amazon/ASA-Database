/**
 * required-fields.js
 * 
 * DEPRECATED: Client-side validation removed in favor of server-side validation.
 * 
 * Server-side validation now enforces:
 * - specimenNumber (required for catalogNumber generation)
 * - year (required for catalogNumber generation)
 * - locality (required for catalogNumber generation)
 * - sex field validation (must be 'male', 'female', or '.')
 * 
 * This file is kept for backwards compatibility but does nothing.
 * It can be safely removed in the future.
 */

// No client-side validation needed - server-side validation handles everything
