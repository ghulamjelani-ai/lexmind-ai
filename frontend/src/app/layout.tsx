import type { Metadata } from "next";
import { Inter, Fraunces } from "next/font/google";
import "./globals.css";
import { ToastProvider } from "@/components/toast";
import { AuthProvider } from "@/lib/auth-context";
import { I18nProvider } from "@/lib/i18n";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://lexmind-ai-iota.vercel.app";
const TITLE = "LexMind — AI legal intelligence for Pakistani law chambers";
const DESCRIPTION =
  "Case management, AI drafting and legal research grounded in official Pakistani sources. Every AI output is a draft, cited and flagged for a lawyer to verify.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: TITLE,
    template: "%s · LexMind",
  },
  description: DESCRIPTION,
  applicationName: "LexMind",
  keywords: [
    "law chamber software Pakistan",
    "legal case management",
    "AI legal research",
    "Pakistan law firm software",
    "legal drafting AI",
    "FBR tax",
  ],
  authors: [{ name: "LexMind" }],
  openGraph: {
    type: "website",
    siteName: "LexMind",
    url: SITE_URL,
    title: TITLE,
    description: DESCRIPTION,
    locale: "en_PK",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
  robots: { index: true, follow: true },
};

// Runs before paint: apply the saved theme so there is no light/dark flash.
const themeScript = `(function(){try{var t=localStorage.getItem('lexmind-theme');if(t==='dark'||t==='light'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${fraunces.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-full flex flex-col">
        <I18nProvider>
          <ToastProvider>
            <AuthProvider>{children}</AuthProvider>
          </ToastProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
