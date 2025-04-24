/**
 * @metadata
 * @description Configuration file for next-intl library
 * @koios_ref CORUJA-I18N-CONFIG-002
 * @references 
 * - `mdc:website/i18n.config.ts` (i18n configuration)
 * - `mdc:website/src/middleware.ts` (i18n routing middleware)
 */

/** @type {import('next-intl').NextIntlConfig} */
module.exports = {
  // List of all locales that are supported
  locales: ['en', 'pt'],
  
  // Used when no locale matches
  defaultLocale: 'en',
  
  // Specify the path to your translations
  // This is the recommended approach for App Router
  // https://next-intl.dev/docs/getting-started/app-router
  localePrefix: 'as-needed',
  
  // Define the domains for each locale (optional)
  // domains: [
  //   {
  //     domain: 'example.com',
  //     defaultLocale: 'en'
  //   },
  //   {
  //     domain: 'example.pt',
  //     defaultLocale: 'pt'
  //   }
  // ]
};
