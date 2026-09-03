import Script from "next/script";
import "./globals.css";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "";
const apiKey = process.env.NEXT_PUBLIC_API_KEY || "";

export const metadata = {
  title: "Space Center Analysis & Monitoring",
  description: "Mission control dashboard for real-time space weather analysis and monitoring."
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Script id="api-config" strategy="beforeInteractive">
          {`window.__API_BASE__ = ${JSON.stringify(apiBase)}; window.__API_KEY__ = ${JSON.stringify(apiKey)};`}
        </Script>
        {children}
      </body>
    </html>
  );
}
