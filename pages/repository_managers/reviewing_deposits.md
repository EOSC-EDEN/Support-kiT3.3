---
title: Reviewing deposits – file formats and technical data quality
description: Check that deposited files are technically sound, complete and fit for long-term preservation.
page_id: reviewing_deposits
order: 2
kind: how-to
story:
  as: manager
  want: review incoming deposits for file formats and technical data quality
  task: review an incoming deposit   # short label for the home-page picker
  so_that: what we ingest is technically sound, complete and fit for long-term preservation
disciplines: [all]
data_types: [all]
keywords: [data review, deposit, data quality]
cpps: [CPP-001, CPP-002, CPP-003, CPP-004, CPP-007, CPP-010, CPP-012, CPP-020, CPP-023, CPP-024, CPP-025, CPP-026, CPP-027, CPP-030]
cpps_primary: [CPP-010, CPP-002, CPP-007]   # the 1-3 processes this module mainly teaches; must also be in cpps
satisfies:
  - {framework: cts-2026, code: R01}
  - {framework: cts-2026, code: R03}
  - {framework: cts-2026, code: R04}
contributors: [Anna-Lena Flügel]
related_pages:
  Researchers: [preparing_deposits]
status: draft
page_citation: true
---

For a data repository manager, technical data quality is primarily about whether the deposited files are technically sound, complete, usable, and suitable for long-term preservation and reuse. It is distinct from assessing whether the scientific content or methodology is correct.

Reviewing deposits includes checking file formats, readability, file and folder structures, naming conventions, encoding, data types, dates, units, missing-value conventions, internal consistency, and the consistency between data and metadata. Corrupted, incomplete, duplicate, obsolete, or technically problematic files need to be identified, and dependencies and preservation risks assessed. Request clarification or remediation from depositors where necessary, apply appropriate automated validation, and document any technical quality issues and actions taken.

## Considerations

Key aspects to consider include:

- File integrity and readability (e.g. files can be opened and read without errors or corruption, checksums)
- File formats and sustainability (e.g. avoid obsolete, uncommon, proprietary formats)
- File structure and organisation (e.g. file and directory names are consistent and meaningful)
- Completeness of the deposited data (e.g. files required to understand and reuse the dataset are actually present)
- Internal consistency (e.g. inconsistent units of measurement, different coding schemes for categorical variables)
- Data structure and machine readability (e.g. consistent columns and data types, valid syntax, references and identifiers resolve correctly)
- Character encoding and language (e.g. encoding is known and appropriate, preferably UTF-8 where suitable)
- Dates, numbers, units, and missing values
- Metadata-to-data consistency
- Versioning and provenance
- Compression and packaging (e.g. archives can be extracted)
- Technical documentation and dependencies (e.g. required software, libraries or packages)
- Automated validation and quality checks (e.g. file format identification, checksums and fixity, virus and malware scanning)
- Preservation risks (e.g. encrypted or password-protected files, unusual hardware or software dependencies, lossy compression)

## Recommendations

- [ ] Perform legal clearance and technical checks to make and keep data accessible.
- [ ] Ensure data integrity at all stages of its life.
- [ ] Check data for technical defects and viruses prior to ingest.
- [ ] Store data in well-supported and preferably non-proprietary file formats.
- [ ] Document data well (e.g. clear explanations, standardised metadata, readme files).
- [ ] Assign unique identifiers to datasets.
- [ ] Identify updates to data or new versions clearly and consistently.

## More information

This module builds upon the following supporting frameworks:

- EOSC EDEN T1.2, Lindlar, M., Caron, B., et al. (2025). *EOSC EDEN M1.1 – Report on Identification of Core Preservation Processes*. Zenodo. <https://doi.org/10.5281/zenodo.16992452>
- CoreTrustSeal Standards and Certification Board. (2025). *CoreTrustSeal Requirements 2026–2028*. Zenodo. <https://doi.org/10.5281/zenodo.17660463> — R01; R03; R04
