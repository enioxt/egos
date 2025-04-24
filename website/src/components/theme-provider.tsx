'use client'

import * as React from 'react'
import { ThemeProvider as NextThemesProvider, type ThemeProviderProps } from 'next-themes'

/**
 * @metadata
 * @description Provides theme context (light/dark mode) using next-themes.
 * @koios_ref KOIOS-WEB-COMP-001
 * @see [next-themes documentation](https://github.com/pacocoursey/next-themes)
 * @references
 * - `mdc:website/src/app/layout.tsx#L4` (Imported and used)
 * - `mdc:website/src/app/globals.css#L34` (Defines .dark variables)
 */
export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
