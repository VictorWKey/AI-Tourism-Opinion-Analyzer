/**
 * Sentry Error Reporting — Renderer Process
 * ============================================
 * Initializes Sentry in the React renderer process.
 * Must be called before React renders.
 *
 * Also exports an ErrorBoundary component that catches React rendering errors
 * and reports them to Sentry.
 */

import * as Sentry from '@sentry/react';

// Must match the DSN used in the main process
const SENTRY_DSN = process.env.SENTRY_DSN || '';

let initialized = false;

/**
 * Initialize Sentry for the renderer process.
 * Call this before React.createRoot().
 */
export function initSentryRenderer(): void {
  if (!SENTRY_DSN || initialized) {
    return;
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: 'production',
    
    // Reduce noise: only enable in production
    enabled: typeof window !== 'undefined',

    // Capture 100% of errors
    sampleRate: 1.0,

    // Performance monitoring (optional)
    tracesSampleRate: 0,

    integrations: [
      // Capture React component tree in errors
      Sentry.browserTracingIntegration(),
    ],

    // Filter out sensitive data
    beforeSend(event) {
      // Strip user paths from stack traces
      if (event.exception?.values) {
        for (const exception of event.exception.values) {
          if (exception.stacktrace?.frames) {
            for (const frame of exception.stacktrace.frames) {
              if (frame.filename) {
                frame.filename = frame.filename.replace(
                  /([A-Z]:\\Users\\)[^\\]+/gi,
                  '$1<user>'
                );
              }
            }
          }
        }
      }
      return event;
    },

    initialScope: {
      tags: {
        process: 'renderer',
      },
    },
  });

  initialized = true;
  console.log('[Sentry] Renderer error reporting initialized');
}

/**
 * Sentry React Error Boundary — wraps your <App /> to catch render crashes.
 * 
 * Usage:
 *   <SentryErrorBoundary fallback={<ErrorFallback />}>
 *     <App />
 *   </SentryErrorBoundary>
 */
export const SentryErrorBoundary = Sentry.ErrorBoundary;

/**
 * Manually capture an exception in the renderer
 */
export function captureRendererException(error: unknown, context?: Record<string, unknown>): void {
  if (!initialized) return;
  
  Sentry.withScope((scope) => {
    if (context) {
      scope.setExtras(context);
    }
    Sentry.captureException(error);
  });
}
