---
track: managers
discipline: Repository & Archive Managers #2
order: 2
name: Reviewing deposits - file formats and technical data quality
description: For a data repository manager, technical data quality is primarily about whether the deposited files are technically sound, complete, usable, and suitable for long-term preservation and reuse. It is distinct from assessing whether the scientific content or methodology is correct.
Reviewing deposits includes checking file formats, readability, file and folder structures, naming conventions, encoding, data types, dates, units, missing-value conventions, internal consistency, and the consistency between data and metadata. Corrupted, incomplete, duplicate, obsolete, or technically problematic files need to be identified, and dependencies and preservation risks need to be assessed. Request clarification or remediation from depositors where necessary. Apply appropriate automated validation and document any technical quality issues and actions taken.
  - data review
  - data quality
  - deposits
---

#### Sections
[Considerations](#considerations) | [Recommendations](#recommendations) | [More information](#more-information) | [Authors](#authors)

### Considerations

Key aspects to consider include:
 
- File integrity and readability (e.g. files can be opened and read without errors or corruption, checksums)
- File formats and sustainability (e.g. avoid obsolete, uncommon, proprietary formats)
- File structure and organisation (e.g. file and directory names are consistent and meaningful)
- Completeness of the deposited data (e.g. check that files required to understand and reuse the dataset are actually present)
- Internal consistency (e.g. inconsistent units of measurement, different coding schemes for categorical variables)
- Data structure and machine readability (e.g. consistent columns, consistent data types, valid syntax, references and identifiers resolve correctly)
- Character encoding and language (e.g. encoding is known and appropriate, preferably UTF-8 where suitable)
- Dates, numbers, units, and missing values
- Metadata-to-data consistency
- Versioning and provenance
- Compression and packaging (e.g. archives can be extracted)
- Technical documentation and dependencies (e.g. required software, libraries or packages)
- Automated validation and quality checks (e.g. file format identification, checksums/fixity, virus/malware scanning)
- Preservation risks (e.g. encrypted or password-protected files, unusual hardware/software dependencies, lossy compression)


### Recommendations

- Perform legal clearance and technical checks to make and keep data accessible.
- Data integrity should be ensured at all stages of its life.
- Data should be checked for technical defects and viruses prior to ingest.
- Data should be stored in well-supported and preferably non-proprietary file formats.
- Data should be well documented (e.g. clear explanations, standardized metadata, readme files).
- Datasets should be assigned unique identifiers.
- Updates to data or new versions should be clearly and consistently identified.


### More information

This module builds upon the following supporting frameworks:

- EOSC EDEN T1.2, Lindlar, M., Caron, B., Benauer, M., Kylander, J., Dekeyser, K., Addis, M., Levlin, M., Laukkanen, M., Lehtonen, J., Burger, F., Koho, T., Schwab, F., Molloy, L., & Zhang, F. (2025). EOSC EDEN M1.1 Report on Identification of Core Preservation Processes. Zenodo. https://doi.org/10.5281/zenodo.16992452 CPPs 001; 002; 003; 004; 007; 010; 012; 020; 023; 024; 025; 026; 027; 030

- CoreTrustSeal Standards and Certification Board. (2025). CoreTrustSeal Requirements 2026-2028. Zenodo. https://doi.org/10.5281/zenodo.17660463  R01; R03; R04


### Authors

Anna-Lena Flügel (https://orcid.org/0000-0001-8218-9609)

[Go to top](#)
