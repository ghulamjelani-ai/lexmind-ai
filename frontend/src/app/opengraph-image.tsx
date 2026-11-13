import { ImageResponse } from "next/og";

export const alt = "LexMind — AI legal intelligence for Pakistani law chambers";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "linear-gradient(135deg, #0b1b3a 0%, #12294f 100%)",
          padding: "72px",
          fontFamily: "sans-serif",
        }}
      >
        {/* Brand mark */}
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: 16,
              background: "rgba(231,178,76,0.15)",
              border: "2px solid #e7b24c",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 36,
            }}
          >
            ⚖️
          </div>
          <div style={{ display: "flex", fontSize: 40, fontWeight: 700, color: "#ffffff" }}>
            Lex<span style={{ color: "#e7b24c" }}>Mind</span>
          </div>
        </div>

        {/* Headline */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div style={{ fontSize: 68, fontWeight: 700, color: "#ffffff", lineHeight: 1.1, maxWidth: 920 }}>
            Legal intelligence your chamber can trust.
          </div>
          <div style={{ fontSize: 30, color: "rgba(255,255,255,0.75)", maxWidth: 940, lineHeight: 1.4 }}>
            Case management, AI drafting and research grounded in official Pakistani sources —
            every output cited and verified by a lawyer.
          </div>
        </div>

        {/* Footer strip */}
        <div style={{ display: "flex", gap: "40px", fontSize: 24, color: "rgba(231,178,76,0.9)" }}>
          <span>Verify-before-use</span>
          <span>Tenant isolation</span>
          <span>Non-fabrication by design</span>
        </div>
      </div>
    ),
    { ...size },
  );
}
