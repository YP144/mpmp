// Merge into your existing next.config.(ts|js|mjs)
// Browser -> Next.js (:3000) -> FastAPI (127.0.0.1:8000)
// "afterFiles" means Next.js' own pages / app/api routes win first,
// everything else under /api is proxied to FastAPI.
const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig = {
  allowedDevOrigins: [
    'mpxo--3000--yosep-setiyanto.apps.axstudio.lge.com',
    'mpxo--3000--yudhis-ranggawidjaya.apps.axstudio.lge.com',
    '*.apps.axstudio.lge.com',
    'https://mpxo-dev.apps.axstudio.lge.com/',
  ],
  async rewrites() {
    return {
      afterFiles: [
        { source: "/api/:path*", destination: `${BACKEND_URL}/api/:path*` },
      ],
    };
  },
};

export default nextConfig;
