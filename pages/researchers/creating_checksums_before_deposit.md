---
title: Creating checksums before deposit
description: Record a checksum for every file so you and the repository can prove nothing changed.
page_id: creating_checksums_before_deposit
kind: how-to
story:
  as: researcher
  want: create checksums for my files before I deposit them
  so_that: the repository can confirm the files arrived exactly as I sent them
disciplines: [all]
data_types: [all]
keywords: [checksums, fixity, integrity, deposit]
cpps: [CPP-001, CPP-002, CPP-003]
cpps_primary: [CPP-001, CPP-002]
satisfies:
  - {framework: cts-2026, code: R14}
contributors: [Arijit Laik]
related_pages:
  Researchers: [preparing_deposits]
status: ready
page_citation: true
gdoc: 1RlROFyqGDQDE0bd0H2lDmi7eyqfZVcl3u3TKI9caUDE
---

A checksum is a short fingerprint of a file. If even one bit of the file changes, the checksum changes too.

Creating checksums before you deposit gives you and the repository a simple way to prove that your files arrived intact and stay that way.

## Considerations

Key aspects to consider include:

- Which checksum algorithm does the repository expect (for example SHA-256 or MD5)?
- Where will you keep the checksum file so it travels with the data?

## Recommendations

- [ ] Generate a SHA-256 checksum for every file, for example with sha256sum or a tool such as Fixity.
- [ ] Save the checksums in a manifest file next to the data and include it in your deposit.

## More information

- Digital Preservation Coalition. Digital Preservation Handbook: Fixity and checksums. <https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums>
