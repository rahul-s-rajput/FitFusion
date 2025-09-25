import nextPWA from "@ducanh2912/next-pwa";

const isDev = process.env.NODE_ENV === "development";
const forceEnablePWA = process.env.NEXT_PUBLIC_ENABLE_PWA === "true";

const withPWA = nextPWA({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: isDev && !forceEnablePWA,
  cacheOnFrontEndNav: true,
  aggressiveFrontEndNavCaching: true,
  reloadOnOnline: false,
  swcMinify: true,
  workboxOptions: {
    disableDevLogs: true,
    maximumFileSizeToCacheInBytes: 10 * 1024 * 1024,
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/.*\.hf\.space\/api\/.*/i,
        handler: "NetworkFirst",
        options: {
          cacheName: "ai-api-cache",
          networkTimeoutSeconds: 30
        }
      }
    ]
  }
});

/** @type {import("next").NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["your-cdn.com"]
  }
};

export default withPWA(nextConfig);
