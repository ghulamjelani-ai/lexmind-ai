import { LegalPage, Section } from "@/components/legal-page";

export const metadata = {
  title: "Terms of Service — LexMind",
  description: "The terms that govern your use of LexMind.",
};

export default function TermsPage() {
  return (
    <LegalPage title="Terms of Service" updated="12 November 2026">
      <p>
        These Terms of Service (&quot;Terms&quot;) govern your access to and use of LexMind (the
        &quot;Service&quot;). By creating a chamber or using the Service, you agree to these Terms. If
        you are accepting on behalf of a chamber or firm, you confirm you are authorised to do so.
      </p>

      <Section heading="1. The Service">
        <p>
          LexMind provides case, client and document management together with AI-assisted drafting and
          legal research tools for legal professionals. The Service is a workspace and assistant — it
          does not practise law and does not provide legal advice.
        </p>
      </Section>

      <Section heading="2. Eligibility & accounts">
        <p>
          You must be a legal professional (or act under the supervision of one) and provide accurate
          registration details. You are responsible for your account, your chamber&apos;s users, and all
          activity under them, and for keeping credentials secure. Enable multi-factor authentication
          where offered.
        </p>
      </Section>

      <Section heading="3. AI output — verify before use">
        <p>
          Every AI-generated output — drafts, summaries, research and citations — is provided as a{" "}
          <strong>draft for a qualified lawyer to review</strong>. It may be incomplete or wrong. You
          must independently verify all content, and all citations against official sources, before
          relying on it, advising a client, or filing anything. You remain solely responsible for all
          professional work product.
        </p>
      </Section>

      <Section heading="4. Acceptable use">
        <p>
          You agree not to misuse the Service: no unlawful activity, no attempts to breach security or
          access other chambers&apos; data, no uploading of malware, and no use that infringes others&apos;
          rights. You are responsible for having the right to upload and process the data you put into
          the Service.
        </p>
      </Section>

      <Section heading="5. Your data">
        <p>
          You retain ownership of the data and documents you upload. You grant LexMind the limited
          rights needed to host and process that data to provide the Service, including sending content
          to third-party AI providers to generate responses. Our handling of personal data is described
          in our Privacy Policy.
        </p>
      </Section>

      <Section heading="6. Fees & billing">
        <p>
          Paid plans are billed in advance for the period shown at checkout. Fees are non-refundable
          except where required by law. We may change pricing with reasonable notice; changes do not
          affect the current paid period.
        </p>
      </Section>

      <Section heading="7. Intellectual property">
        <p>
          LexMind and its software, branding and content are owned by us and our licensors. These Terms
          grant you a limited, non-exclusive, non-transferable right to use the Service; no other rights
          are granted.
        </p>
      </Section>

      <Section heading="8. Disclaimers & limitation of liability">
        <p>
          The Service is provided &quot;as is&quot; without warranties of any kind. To the maximum extent
          permitted by law, LexMind is not liable for any indirect or consequential loss, or for any
          loss arising from reliance on AI output that was not independently verified. Nothing limits
          liability that cannot be limited by law.
        </p>
      </Section>

      <Section heading="9. Suspension & termination">
        <p>
          You may stop using the Service at any time. We may suspend or terminate access for breach of
          these Terms or to protect the Service or its users. On termination you may export your data
          for a reasonable period, after which it may be deleted.
        </p>
      </Section>

      <Section heading="10. Governing law">
        <p>
          These Terms are governed by the laws of the Islamic Republic of Pakistan, and the courts of
          Pakistan have jurisdiction, unless otherwise agreed in writing.
        </p>
      </Section>

      <Section heading="11. Changes & contact">
        <p>
          We may update these Terms; material changes will be notified through the Service. Continued
          use after changes means you accept them. Questions about these Terms can be sent to your
          chamber&apos;s LexMind contact.
        </p>
      </Section>
    </LegalPage>
  );
}
