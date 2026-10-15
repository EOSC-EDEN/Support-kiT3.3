EDEN Support-kit module template  
*Worked example: the "Preparing deposits" module written in the template. Copy the blank template for a new module, not this one.*  
Write one support-kit module in this document, then export it as Markdown. A short script turns the export into a module page for the kit.

# **How to use this template**

> 1. Make your own copy: File \> Make a copy. Name the copy after your module.  
> 2. Fill in the table under **Module metadata**. Replace every text in \[square brackets\]. Leave a row empty if it does not apply.  
> 3. Write the module under **Module content**. Keep the section headings (Heading 2), change their text if you need to, and add more Heading 2 or Heading 3 sections as needed.  
> 4. In **Recommendations**, write one action per bullet. They become a checklist readers can tick.  
> 5. Share the copy with your WP3 colleagues for comments. When it is ready: File \> Download \> Markdown (.md).  
> 6. Put the .md file in the kit repository and run **python3 var/gdoc\_to\_module.py your-file.md**. The script writes the module page into the right folder and reports anything missing.

Keep headings and lists as real Google Docs headings and bullets (not bold text or typed dashes), so the Markdown export keeps them.

# **Module metadata**

| Field | Value | How to fill it |
| :---- | :---- | :---- |
| Title | Checking incoming file formats | What the module is about, task first, under 8 words. Example: Preparing deposits |
| Description | Make your files sustainable, documented and technically sound before you hand them to a repository. | One sentence shown on cards and in search results. |
| Role | Repository manager (curator) | Who it is for: researcher, manager, trainer, or anyone. |
| I want to | As a manager, I want to prepare my files for deposit, with sustainable formats, documentation and basic technical checks | The user story. Start lower case, no full stop. Example: prepare my files for deposit, with sustainable formats and basic checks |
| So that | the dataset stays accessible, understandable and reusable beyond the original project | The benefit. It should add something the title does not already say. |
| Short task | prepare my files for deposit | Under 45 characters. Shown in the home page's "I want to…" menu. |
| Kind of help | Get it done (how-to) | how-to (get it done), tutorial (learn by doing), reference (look it up) or explanation (understand why). |
| Order in the role path | 2nd | Position among the modules for this role. A number. |
| Disciplines | all | Comma-separated, or all. |
| Data types | all | Comma-separated, or all. |
| Keywords | deposit, planning, preparations | Comma-separated. Used by search. |
| Processes it mainly teaches | File format validation, checksum validaton, virus scan, Replication | 1 to 3 WP1 Core Preservation Process IDs, comma-separated. List: eosc-eden.github.io/wp1-cpp-descriptions |
| Other processes it applies | Integrity checking; 999 | Other CPP IDs the module touches. Keep it to the ones a reader would act on. |
| Frameworks cited | CoreTrustSeal R14 R09; nestor; FAIRish thing; ISO 16363: 4.2 | framework: requirement codes, separated by semicolons. Frameworks: cts-2023, cts-2026, nestor, iso-16363, oais, premis, eosc-tf-fm. |
| Related modules | Reviewing deposits – file formats and technical data quality, Unknown module | File names of related modules, comma-separated. |
| Contributors | [Anna-Lena Flügel](mailto:alf@example.org), New Person | Names as listed in the kit's contributor list (with ORCID). Comma-separated. |
| Status | Ready for review | draft or ready. |

# **Module content**

Considering data preservation and reusability during preparation helps ensure that the dataset remains accessible, understandable, and usable beyond the original research project. Good preparation, such as using sustainable formats, documenting data structures, and recording processing steps, reduces the risk of data becoming inaccessible, ambiguous, or unusable over time.

## **Considerations**

Key aspects to consider include:

> * Did you review the data you plan to deposit (e.g. are all necessary files included and unnecessary or redundant files removed? Which are raw, processed, derived, or final data?)  
> * Are the file formats appropriate (e.g. widely used and supported, non-proprietary if possible)?  
> * Is technical file quality ok (e.g. files open correctly, completeness, coherent and clear file names)?  
> * Is the data machine-readable (e.g. consistent data types, consistent representations of missing values, units of measurement included)?  
> * Is the data sufficiently and clearly explained and documented (e.g. a readme\_file.txt)?

## **Recommendations**

> * Check and follow the deposit guidelines of the repository you chose for your data deposit.  
> * Familiarise yourself with (meta)data standards and conventions within your discipline, and use them consistently.  
> * Think about future re-use: does the dataset contain all the information someone else would need?

## **More information**

This module builds upon the following supporting frameworks:

> * CoreTrustSeal Standards and Certification Board. (2025). *CoreTrustSeal Requirements 2026–2028*. Zenodo. [https\://doi.org/10.5281/zenodo.17660463](https://doi.org/10.5281/zenodo.17660463), R14  
> * EOSC EDEN T1.2, Lindlar, M., Caron, B., et al. (2025). *EOSC EDEN M1.1 – Report on Identification of Core Preservation Processes*. Zenodo. https\://doi.org/10.5281/zenodo.16992452