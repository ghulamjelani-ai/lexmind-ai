import type { NextConfig } from "next";

// Where to proxy /api/* to. In production (Vercel) this defaults to the Railway
// API; set API_PROXY_TARGET to override (e.g. http://localhost:8000 for local).
const API_PROXY_TARGET =
  process.env.API_PROXY_TARGET || "https://lexmind-api-production-6af40992.up.railway.app";

const nextConfig: NextConfig = {
  // Produce a self-contained server build for the Docker image.
  output: "standalone",
  // Hide the dev-only on-screen indicator (the floating "N" / insights badge).
  devIndicators: false,
  // Proxy API calls through the web origin so the session cookie is FIRST-PARTY.
  // The browser only ever talks to this app's own origin, which sidesteps modern
  // browsers blocking third-party (cross-site) cookies when the API is on a
  // different domain. See also api.ts (it calls same-origin /api/v1 in the browser).
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${API_PROXY_TARGET}/api/:path*` },
    ];
  },
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
