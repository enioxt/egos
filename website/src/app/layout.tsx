import type { Metadata } from 'next';
import { Inter, EB_Garamond } from 'next/font/google';
import { cn } from '@/lib/utils';
import { ThemeProvider } from '@/components/theme-provider';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: '--font-inter' });
const garamond = EB_Garamond({
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-garamond'
});

// Basic Metadata - Should be refined per page
export const metadata: Metadata = {
  title: "EGOS - Ethical Generative Operating System",
  description: "EGOS Project - Open Source Ethical AI Framework",
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: Readonly<RootLayoutProps>) {
  return (
    <html lang="en" className={`${inter.variable} ${garamond.variable}`} suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          inter.variable,
          garamond.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="relative flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
