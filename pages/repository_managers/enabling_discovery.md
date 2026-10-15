---
title: Enabling discovery and identification
description: Assign identifiers and machine-discoverable metadata so users can find, interpret and reuse datasets.
page_id: enabling_discovery
order: 1
kind: how-to
story:
  as: manager
  want: make the datasets in my repository discoverable and uniquely identifiable
  task: make our datasets findable   # short label for the home-page picker
  so_that: users can find, interpret and reuse them, and research becomes more transparent
disciplines: [all]
data_types: [all]
keywords: [pid, TDR, machine-actionable]
cpps: [CPP-005, CPP-009, CPP-011, CPP-013, CPP-016, CPP-019, CPP-021, CPP-024, CPP-028]
cpps_primary: [CPP-024, CPP-005]   # the 1-3 processes this module mainly teaches; must also be in cpps
satisfies:
  - {framework: cts-2023, code: R10}
  - {framework: cts-2023, code: R12}
  - {framework: eosc-tf-fm, code: FRM-07}
  - {framework: eosc-tf-fm, code: FRM-08}
contributors: [Camilla Hagen Blixhavn]
rdmkit:
  - name: Data discoverability
    url: https://rdmkit.elixir-europe.org/data_discoverability
status: draft
page_citation: true
---

To facilitate reuse of data, we need to first make data discoverable. Data discoverability involves assigning identifiers and metadata to a dataset to allow users to query, find, interpret, and reuse it. Choosing an appropriate repository, improving file structure, providing documentation, and producing machine-discoverable metadata are all part of this process.

## Considerations

- Consider where to publish your data for improved discoverability: in a discipline-specific or agnostic repository, and preferably in a Trustworthy Digital Repository (TDR).
- Consider how you structure data into levels of datasets and files, to decide what will be assigned an identifier and to support meaningful discovery.
- Consider which terms you use to describe the dataset (e.g. title, abstract, metadata) so they align with a user's search terms.
- Consider what a user will need to know to interpret and reuse a dataset, and include that information together with the dataset.

## Recommendations

- [ ] Assign unique, persistent identifiers (PIDs) to datasets (REC-12).
- [ ] Use PIDs on both dataset and file level (FRM-08).
- [ ] Document data well, e.g. clear explanations, metadata and readme files (REC-05).
- [ ] Provide machine-discoverable and interpretable metadata about both deposits (identifiers, authorship) and deposit content (quality, experimental conditions, variables measured) (FRM-07).

## More information

This module builds upon the following supporting frameworks:

- CoreTrustSeal requirements: R10; R12
- Core Preservation Processes (EOSC EDEN M1.1): see the list below
- EOSC-A TF FAIR Metrics and Digital Objects: FRM-07; FRM-08
