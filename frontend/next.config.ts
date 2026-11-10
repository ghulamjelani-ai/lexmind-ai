import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produce a self-contained server build for the Docker image.
  output: "standalone",
  // Hide the dev-only on-screen indicator (the floating "N" / insights badge).
  devIndicators: false,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
