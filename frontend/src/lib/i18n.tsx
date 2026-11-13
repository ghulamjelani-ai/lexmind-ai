"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

export type Locale = "en" | "ur" | "ar";

export const LOCALES: { code: Locale; label: string; native: string; rtl: boolean }[] = [
  { code: "en", label: "English", native: "English", rtl: false },
  { code: "ur", label: "Urdu", native: "اردو", rtl: true },
  { code: "ar", label: "Arabic", native: "العربية", rtl: true },
];

// Translations for the public (marketing + auth) surface. The dashboard stays
// English for now, so new locales never produce a half-translated screen.
const DICT: Record<string, Record<Locale, string>> = {
  "nav.features": { en: "Features", ur: "خصوصیات", ar: "المميزات" },
  "nav.how": { en: "How it works", ur: "یہ کیسے کام کرتا ہے", ar: "كيف يعمل" },
  "nav.security": { en: "Security", ur: "سیکیورٹی", ar: "الأمان" },
  "nav.pricing": { en: "Pricing", ur: "قیمتیں", ar: "الأسعار" },
  "nav.signin": { en: "Sign in", ur: "سائن اِن", ar: "تسجيل الدخول" },
  "nav.startFree": { en: "Start free", ur: "مفت شروع کریں", ar: "ابدأ مجانًا" },
  "auth.signin": { en: "Sign in", ur: "سائن اِن", ar: "تسجيل الدخول" },
  "auth.welcomeBack": { en: "Welcome back", ur: "خوش آمدید", ar: "مرحبًا بعودتك" },
  "auth.subtitle": {
    en: "Sign in to your chamber workspace.",
    ur: "اپنے چیمبر ورک اسپیس میں سائن اِن کریں۔",
    ar: "سجّل الدخول إلى مساحة عمل مكتبك.",
  },
  "auth.chamberId": { en: "Chamber ID", ur: "چیمبر آئی ڈی", ar: "معرّف المكتب" },
  "auth.email": { en: "Email", ur: "ای میل", ar: "البريد الإلكتروني" },
  "auth.password": { en: "Password", ur: "پاس ورڈ", ar: "كلمة المرور" },
  "auth.signinBtn": { en: "Sign in", ur: "سائن اِن کریں", ar: "تسجيل الدخول" },
  "auth.signingIn": { en: "Signing in…", ur: "سائن اِن ہو رہا ہے…", ar: "جارٍ تسجيل الدخول…" },
  "auth.forgotPw": { en: "Forgot password?", ur: "پاس ورڈ بھول گئے؟", ar: "نسيت كلمة المرور؟" },
  "auth.createChamber": { en: "Create a chamber", ur: "نیا چیمبر بنائیں", ar: "إنشاء مكتب" },
  "auth.forgotChamber": { en: "Forgot your Chamber ID?", ur: "اپنا چیمبر آئی ڈی بھول گئے؟", ar: "نسيت معرّف المكتب؟" },
};

interface I18nValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
  rtl: boolean;
}

const I18nContext = createContext<I18nValue | null>(null);
const STORAGE_KEY = "lexmind-locale";

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY) as Locale | null;
      if (saved && LOCALES.some((l) => l.code === saved)) setLocaleState(saved);
    } catch {
      /* ignore */
    }
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    try {
      localStorage.setItem(STORAGE_KEY, l);
    } catch {
      /* ignore */
    }
  }, []);

  const rtl = LOCALES.find((l) => l.code === locale)?.rtl ?? false;

  const t = useCallback(
    (key: string) => DICT[key]?.[locale] ?? DICT[key]?.en ?? key,
    [locale],
  );

  return <I18nContext.Provider value={{ locale, setLocale, t, rtl }}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  // Safe fallback so components work even outside a provider (English, LTR).
  if (!ctx) return { locale: "en", setLocale: () => {}, t: (k) => DICT[k]?.en ?? k, rtl: false };
  return ctx;
}
