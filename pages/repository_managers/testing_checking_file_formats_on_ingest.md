---
title: Testing Checking file formats on ingest
description: Identify and validate file formats when data arrives, before it is archived.
page_id: testing_checking_file_formats_on_ingest
kind: how-to
story:
  as: manager
  want: check the formats of incoming files before ingest
  so_that: files that cannot be opened or preserved are caught before they are archived
disciplines: [all]
data_types: [all]
keywords: [file formats, PRONOM, validation, ingest]
cpps: [CPP-007, CPP-008, CPP-010, CPP-029]
cpps_primary: [CPP-008, CPP-010]
satisfies:
  - {framework: cts-2026, code: R14}
  - {framework: nestor}
contributors: [Arijit Laik]
related_pages:
  Repository_managers: [reviewing_deposits]
status: draft
page_citation: true
gdoc: 1lQgV3HzBwCLsDHE_ld1VOU8eQ--QiPkFloZrZFmTNn4
---

Files arrive in many formats, and some of them will not open in ten years. Checking formats at ingest tells you what you hold, catches broken files early and gives preservation planning something to work with.

## Considerations

Key aspects to consider include:

- Which formats does the repository accept, and which does it only keep as deposited?
- What happens to a file that cannot be identified or fails validation?

## Recommendations

- [ ] Identify every file with a format registry such as PRONOM, using a tool like DROID or Siegfried.
- [ ] Validate formats that have validators (for example JHOVE or veraPDF) and record the result.
- [ ] Ask the depositor about files that cannot be identified before accepting them.

## More information

- The National Archives (UK). PRONOM technical registry. <https://www.nationalarchives.gov.uk/PRONOM/>
