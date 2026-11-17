---
title: Verifying checksums after transfer
description: Check that every file still matches its checksum after it has been copied or uploaded.
page_id: verifying_checksums_after_transfer
kind: how-to
story:
  as: manager
  want: verify checksums of files after they are transferred to the repository
  so_that: damaged or incomplete transfers are caught before the files are archived
disciplines: [all]
data_types: [all]
keywords: [checksums, fixity, transfer, ingest]
cpps: [CPP-002, CPP-007, CPP-029]
cpps_primary: [CPP-002]
satisfies:
  - {framework: cts-2026, code: R14}
contributors: [Arijit Laik]
related_pages:
  Repository_managers: [reviewing_deposits]
status: ready
page_citation: true
gdoc: 1n7abm-GWdqIsyvZfuAk8CFTfyAXOgiW8euMZwDn8DCA
---

Files can be damaged on the way into a repository: a network hiccup or a full disk is enough. Comparing each file with the checksum the depositor sent shows straight away whether anything went wrong.

## Considerations

Key aspects to consider include:

- Did the depositor send a checksum manifest, and in which algorithm?
- What do you do with a file whose checksum does not match?

## Recommendations

- [ ] Recalculate the checksum of every received file with the same algorithm as the manifest.
- [ ] Ask the depositor to send any file again whose checksum does not match, before you ingest it.

## More information

- Digital Preservation Coalition. Digital Preservation Handbook: Fixity and checksums. <https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums>
