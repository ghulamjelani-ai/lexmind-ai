import { LegalPage, Section } from "@/components/legal-page";

export const metadata = {
  title: "Privacy Policy — LexMind",
  description: "How LexMind collects, uses and protects your data.",
};

export default function PrivacyPage() {
  return (
    <LegalPage title="Privacy Policy" updated="12 November 2026">
      <p>
        This Privacy Policy explains what data LexMind (&quot;we&quot;) collects, how we use it, and the
        choices you have. It applies to the LexMind Service. Because LexMind is used by legal
        professionals who handle their clients&apos; information, we treat the data in your chamber as
        confidential and isolated to your chamber.
      </p>

      <Section heading="1. Data we collect">
        <p>
          <strong>Account &amp; chamber data:</strong> your name, email, chamber name and role.
          <br />
          <strong>Content you upload:</strong> cases, clients, documents and messages you add to your
          workspace. This may include sensitive personal data (for example CNICs) that you choose to
          store.
          <br />
          <strong>Usage &amp; technical data:</strong> log and device data such as IP address and
          actions taken, used to operate and secure the Service.
        </p>
      </Section>

      <Section heading="2. How we use data">
        <p>
          To provide and maintain the Service; to authenticate users and enforce permissions; to
          generate AI drafts and research you request; to secure the Service and prevent abuse; and to
          comply with legal obligations. We do not sell your data.
        </p>
      </Section>

      <Section heading="3. AI processing & third parties">
        <p>
          When you use AI features, the relevant content (your prompt and the documents needed to answer
          it) is sent to third-party AI providers to generate a response. Legal research queries may be
          sent to a web-search provider restricted to official sources. These providers process the data
          only to return a result. We select providers that do not use submitted content to train their
          models where that option is available.
        </p>
      </Section>

      <Section heading="4. Storage & security">
        <p>
          Each chamber&apos;s data is isolated using database row-level security, so one chamber cannot
          access another&apos;s. Sensitive fields (such as CNIC and MFA secrets) are encrypted at rest.
          Access is controlled by role-based permissions and protected by multi-factor authentication and
          an audit log. No system is perfectly secure, but we apply reasonable technical and
          organisational measures.
        </p>
      </Section>

      <Section heading="5. Retention">
        <p>
          We keep your data for as long as your chamber is active and as needed to provide the Service.
          After account closure, data is retained for a limited period to allow export, then deleted or
          anonymised, unless the law requires otherwise.
        </p>
      </Section>

      <Section heading="6. Your rights">
        <p>
          You can access, correct or export the data in your chamber through the Service, and request
          deletion of your account. As the chamber owner you control your users&apos; access. Where data
          belongs to your clients, you are the controller and LexMind processes it on your behalf.
        </p>
      </Section>

      <Section heading="7. Cookies & sessions">
        <p>
          We use a strictly necessary, httpOnly session cookie to keep you signed in. We do not use
          third-party advertising or tracking cookies.
        </p>
      </Section>

      <Section heading="8. International transfers">
        <p>
          Our hosting and AI providers may process data outside Pakistan. Where that happens, we rely on
          providers that offer appropriate safeguards for the data they handle.
        </p>
      </Section>

      <Section heading="9. Changes & contact">
        <p>
          We may update this Policy; material changes will be notified through the Service. For privacy
          questions or requests, contact your chamber&apos;s LexMind contact.
        </p>
      </Section>
    </LegalPage>
  );
}
