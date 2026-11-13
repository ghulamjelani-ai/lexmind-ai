import type { MetadataRoute } from "next";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://lexmind-ai-iota.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  return ["", "/login", "/signup", "/privacy", "/terms"].map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: path === "" ? 1 : 0.6,
  }));
}
