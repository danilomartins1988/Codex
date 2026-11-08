# Editorial research and verification status

**Primary-source access is blocked. This episode is not editorially cleared for publication.**

On 2026-11-08, requests to Visa's annual-report website, Visa's VisaNet page,
and Mastercard's FAQ failed with proxy CONNECT 403 errors. No document body was
retrieved. The sources in `claims.json` are references for verification, not
citations to passages that were actually read. Do not describe this research as completed.

The draft narration follows the conventional US four-party card model and
intentionally avoids revenue figures, market shares, transaction volumes and
fee percentages. Every scene maps to a claim ID in `claims.json`.

## Clear the editorial gate

1. Allow the official domains in environment settings (do not disable TLS verification).
2. Fetch the companies' available annual reports / 10-Ks and the VisaNet overview.
3. Record the actual filing year, URL, section, supporting passage, retrieval date,
   and SHA256 of locally retained evidence in `claims.json`.
4. Verify C1–C6 individually before setting their verification flags. A URL
   existing or returning HTTP 200 is not substantive fact verification.
5. Set status to `verified` only after all claims pass. Then run `npm run editorial:check`.

## Scope and qualifications

- Banks generally lend; networks generally connect participants. Products and
  exceptions vary. US four-party consumer credit is the frame of reference.
- An authorization is not clearing or final settlement. The short shows the
  authorization request/response, not a literal movement of loan cash in real time.
- Network stand-in authorization and alternative routing exist. The simplified
  narration describes the usual issuer decision, not every outage scenario.
- Interchange is not the same as the merchant discount, issuer interest income,
  or network revenue. Diagram nodes are **not to scale** and show no percentages.
- Visa and Mastercard have different product offerings, contracts, fee categories
  and risk disclosures. No claim that their models are identical is intended.
- The closing line is a metaphor for a network business, not a claim about asset
  ownership, the absence of all credit exposure, or the accounting of every service.
