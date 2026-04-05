import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    domains: ['pbs.twimg.com', 'abs.twimg.com'],
  },
};

export default nextConfig;
