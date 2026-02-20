/**
 * Sentry Error Reporting — Main Process
 * =======================================
 * Initializes Sentry in the Electron main process for crash and error tracking.
 *
 * SETUP INSTRUCTIONS:
 * 1. Create a free account at https://sentry.io
 * 2. Create a new Electron project
 * 3. Copy your DSN and set it as the SENTRY_DSN environment variable,
 *    or replace the placeholder below.
 *
 * In production builds, set SENTRY_DSN via:
 *   - GitHub Actions secret → injected at build time
 *   - Or hardcode it here (DSNs are not secret — they only allow sending events)
 */

import * as Sentry from '@sentry/electron/main';
import { app } from 'electron';

// The DSN (Data Source Name) tells Sentry where to send events.
// Replace this with your actual Sentry DSN, or set via environment variable.
// DSNs are safe to commit — they only allow sending error events, not reading them.
const SENTRY_DSN = process.env.SENTRY_DSN || '';

/**
 * Initialize Sentry for the main process.
 * Call this as early as possible in main.ts.
 */
export function initSentryMain(): void {
  if (!SENTRY_DSN) {
    console.log('[Sentry] No DSN configured — error reporting disabled');
    return;
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    release: `tourlyai@${app.getVersion()}`,
    environment: app.isPackaged ? 'production' : 'development',
    
    // Only send events in production (avoid noise from dev)
    enabled: app.isPackaged,

    // Adjust sample rates as needed
    // 1.0 = capture 100% of errors, 0.1 = capture 10%
    sampleRate: 1.0,
    
    // Performance monitoring — sample 10% of transactions
    tracesSampleRate: 0.1,

    // Filter out sensitive data before sending
    beforeSend(event) {
      // Strip any file paths that might contain usernames
      if (event.exception?.values) {
        for (const exception of event.exception.values) {
          if (exception.stacktrace?.frames) {
            for (const frame of exception.stacktrace.frames) {
              if (frame.filename) {
                // Normalize paths: C:\Users\John\... → C:\Users\<user>\...
                frame.filename = frame.filename.replace(
                  /([A-Z]:\\Users\\)[^\\]+/gi,
                  '$1<user>'
                );
              }
            }
          }
        }
      }

      // Remove breadcrumbs that might contain dataset content
      if (event.breadcrumbs) {
        event.breadcrumbs = event.breadcrumbs.filter(
          (b) => !b.message?.includes('dataset') && !b.message?.includes('.csv')
        );
      }

      return event;
    },

    // Tags for filtering in Sentry dashboard
    initialScope: {
      tags: {
        process: 'main',
        platform: process.platform,
        arch: process.arch,
      },
    },
  });

  console.log('[Sentry] Main process error reporting initialized');
}
