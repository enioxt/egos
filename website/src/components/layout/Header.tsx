'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Globe, Menu, X, ChevronDown } from 'lucide-react';

// Simplified version that doesn't rely on translations initially
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLangDropdownOpen, setIsLangDropdownOpen] = useState(false);
  const pathname = usePathname();
  // Determine locale from pathname (simplified for now, next-intl handles this)
  const currentLocale = pathname.split('/')[1] || 'en';

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    if (isLangDropdownOpen) setIsLangDropdownOpen(false);
  };

  const toggleLangDropdown = () => {
    setIsLangDropdownOpen(!isLangDropdownOpen);
  };

  // Function to get the non-locale part of the path
  const getCleanPathname = () => {
    if (pathname.startsWith('/en') || pathname.startsWith('/pt')) {
      return pathname.substring(3) || '/'; // Remove /en or /pt
    } 
    return pathname;
  };
  
  const cleanPathname = getCleanPathname();

  return (
    <header className="fixed top-0 left-0 w-full bg-background/80 backdrop-blur-sm shadow-sm z-50 p-4">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo - Assuming EGOS is brand name, not translated */}
        <div>
          <Link href={`/${currentLocale}`} className="text-xl font-serif text-foreground">
            EGOS
          </Link>
        </div>

        {/* Desktop Navigation */} 
        <nav className="hidden md:flex items-center space-x-6">
          <Link href={`/${currentLocale}/#principles`} className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Principles
          </Link>
          <Link href={`/${currentLocale}/#subsystems`} className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Subsystems
          </Link>
          <Link href={`/${currentLocale}/#roadmap`} className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Roadmap
          </Link>
          
          {/* Language Switcher */}
          <div className="relative">
            <button 
              id="lang-switcher-button"
              onClick={toggleLangDropdown}
              className="flex items-center text-muted-foreground hover:text-foreground" 
              aria-haspopup="true"
              aria-expanded={isLangDropdownOpen}
              aria-controls="lang-switcher-dropdown"
              aria-label="Select Language" 
            >
              <Globe className="mr-1 h-4 w-4" />
              <span className="uppercase">{currentLocale}</span> 
              <ChevronDown className={`ml-1 h-3 w-3 transition-transform ${isLangDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {isLangDropdownOpen && (
              <div 
                id="lang-switcher-dropdown"
                className="absolute right-0 mt-2 w-32 bg-background border border-border rounded-md shadow-lg p-1 z-10"
                role="menu"
                aria-labelledby="lang-switcher-button"
              >
                <Link href={cleanPathname} locale="en" onClick={() => setIsLangDropdownOpen(false)} className="block w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded-sm" role="menuitem">English</Link> 
                <Link href={cleanPathname} locale="pt" onClick={() => setIsLangDropdownOpen(false)} className="block w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded-sm" role="menuitem">Portuguese</Link> 
              </div>
            )}
          </div>
        </nav>

        {/* Mobile menu button */} 
        <button 
          className="md:hidden p-2 text-muted-foreground hover:text-foreground" 
          onClick={toggleMenu}
          aria-expanded={isMenuOpen}
          aria-controls="mobile-menu"
          aria-label={isMenuOpen ? 'Close menu' : 'Open menu'} 
        >
          {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />} 
        </button>
      </div>

      {/* Mobile menu */} 
      {isMenuOpen && (
        <nav 
          id="mobile-menu"
          className="md:hidden bg-background py-4 border-t border-border mt-4"
          aria-label="Mobile Navigation" 
        >
          <div className="container mx-auto flex flex-col space-y-1">
            <Link href={`/${currentLocale}/#principles`} onClick={toggleMenu} className="block px-4 py-2 text-muted-foreground hover:text-foreground rounded-md">
              Principles
            </Link>
            <Link href={`/${currentLocale}/#subsystems`} onClick={toggleMenu} className="block px-4 py-2 text-muted-foreground hover:text-foreground rounded-md">
              Subsystems
            </Link>
            <Link href={`/${currentLocale}/#roadmap`} onClick={toggleMenu} className="block px-4 py-2 text-muted-foreground hover:text-foreground rounded-md">
              Roadmap
            </Link>
            <div className="px-4 pt-3 mt-2 border-t border-border">
              <p className="text-sm font-medium text-foreground mb-2">Select Language</p>
              <div className="flex space-x-4">
                 <Link href={cleanPathname} locale="en" onClick={toggleMenu} className="flex items-center text-sm text-muted-foreground hover:text-foreground">
                   <Globe className="mr-1 h-4 w-4" /> English 
                 </Link>
                 <Link href={cleanPathname} locale="pt" onClick={toggleMenu} className="flex items-center text-sm text-muted-foreground hover:text-foreground">
                   <Globe className="mr-1 h-4 w-4" /> Portuguese 
                 </Link>
               </div>
            </div>
          </div>
        </nav>
      )}
    </header>
  );
};

export default Header;
