/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Required for Docker deployment (generates .next/standalone)
  output: 'standalone',

  images: {
    domains: [],
  },
}

module.exports = nextConfig
