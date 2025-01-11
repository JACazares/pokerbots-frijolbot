import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

module.exports = {
  async rewrites() {
    return [
      {
        source: '/analysis/:path*',
        destination: 'http://10.29.251.249:5000/analysis/:path*',
      },
    ];
  },
};

export default nextConfig;
