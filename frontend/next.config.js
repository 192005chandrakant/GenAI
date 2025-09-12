/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'lh3.googleusercontent.com'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ],
      },
    ]
  },
  // Performance optimization for chunks
  webpack: (config, { isServer }) => {
    // Optimize chunk size
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        default: false,
        vendors: false,
        // Vendor chunk for larger libraries
        vendor: {
          name: 'vendor',
          chunks: 'all',
          test: /node_modules/,
          priority: 20,
        },
        // Create specific chunks for larger packages
        firebase: {
          name: 'firebase',
          test: /[\\/]node_modules[\\/](firebase|@firebase)/,
          chunks: 'all',
          priority: 30,
        },
        react: {
          name: 'react',
          test: /[\\/]node_modules[\\/](react|react-dom)/,
          chunks: 'all',
          priority: 40,
        },
      },
    };
    
    return config;
  },
  // Increase timeout for static generation/loading
  staticPageGenerationTimeout: 120,
  experimental: {
    // Apply React optimizations
    optimizeFonts: true,
    optimizeCss: true,
    scrollRestoration: true,
  },
}

module.exports = nextConfig
