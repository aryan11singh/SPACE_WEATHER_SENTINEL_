/** @type {import("next").NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "img-src 'self' https: data:",
              "media-src 'self' https: data:",
              "script-src 'self' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline' https:",
              "connect-src 'self' https:",
              "font-src 'self' https: data:"
            ].join("; ")
          }
        ]
      }
    ];
  },
  async rewrites() {
    const target = process.env.API_PROXY_TARGET || "";
    if (!target) return [];
    return [
      {
        source: "/api/:path*",
        destination: `${target}/api/:path*`
      }
    ];
  }
};

module.exports = nextConfig;
