/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { dev, isServer }) => {
    // Disable Webpack caching on local machine to save RAM memory space
    if (dev) {
      config.cache = false;
    }
    return config;
  },
};

module.exports = nextConfig;