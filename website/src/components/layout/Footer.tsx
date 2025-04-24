'use client';

import { Github, MessageCircle, BookOpen, Globe, Rocket, PanelRight, Heart, Lock, FileText, Languages } from 'lucide-react';
import Link from 'next/link';
import React from 'react';

/**
 * @metadata
 * @description Footer component for the EGOS website. Redesigned using golden ratio principles.
 * @koios_ref KOIOS-WEB-COMP-002
 * @references 
 * - `mdc:website/src/app/layout.tsx` (Usage in main layout)
 * - `mdc:website/src/app/globals.css` (Styling variables)
 */
const Footer = () => {
  const currentYear = new Date().getFullYear();

  const navLinks = [
    { href: "/about", label: "About", icon: Heart },
    { href: "/philosophy", label: "Philosophy", icon: BookOpen },
    { href: "/roadmap", label: "Roadmap", icon: Rocket },
    { href: "/contact", label: "Contact", icon: MessageCircle },
  ];

  const resourceLinks = [
    { href: "/docs", label: "Docs", icon: FileText },
    { href: "/privacy", label: "Privacy", icon: Lock },
  ];

  const socialLinks = [
    { href: "https://github.com/enioxt/egos", label: "GitHub", icon: Github },
  ];

  const renderLinks = (links: { href: string; label: string; icon: React.ElementType }[]) => (
    <ul className="space-y-2">
      {links.map((link) => (
        <li key={link.href}>
          <Link href={link.href} className="flex items-center text-muted-foreground hover:text-foreground transition-colors duration-200">
            <link.icon className="mr-2 h-4 w-4" />
            {link.label}
          </Link>
        </li>
      ))}
    </ul>
  );

  return (
    <footer className="bg-footer-background border-t border-border py-12 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Branding/About */}
          <div className="space-y-4">
            <Link href="/" className="inline-flex items-center text-2xl font-bold text-primary">
              EGOS
            </Link>
            <p className="text-sm text-muted-foreground">
              Exploring the frontiers of consciousness through open technology.
            </p>
          </div>

          {/* Navigation Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-foreground">Navigate</h3>
            {renderLinks(navLinks)}
          </div>

          {/* Resource Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-foreground">Resources</h3>
            {renderLinks(resourceLinks)}
          </div>

          {/* Social Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-foreground">Connect</h3>
            {renderLinks(socialLinks)}
          </div>
        </div>

        <div className="mt-8 border-t border-border pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; {currentYear} EGOS Project. All rights reserved.</p>
          <p className="mt-1">An Enioxt initiative.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
