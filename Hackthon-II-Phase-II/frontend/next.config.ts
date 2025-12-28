import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {}, // ✅ DISABLE turbopack safely

  webpack: (config) => {
    config.resolve.alias["@"] = path.resolve(__dirname);
    return config;
  },
};

export default nextConfig;
