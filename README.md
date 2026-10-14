This demo solution in the main branch should present you with the following functionality as of now: 

## Content
Markdown files with front matter, located in folder articles, are the basis for the web content. The solution is further based on html, vanilla javascript, css styling and json. Github actions is used. AI have been used to produce and check code. 

## Search & Relevance

- Advanced Full-Text Search: Simultaneously searches across the title (name/title), abstract (description/abstract), keywords (keywords/tags), and the actual body content of the modules.
- Smart Weighting & Sorting: Searches automatically score hits in the title higher than hits in the body text, sorting results by relevance. When no search is active, modules are sorted logically by their track and order.
- Search Match Snippets: Automatically generates a text excerpt under each closed module showing exactly where your search term matched. If the match occurs under a specific Markdown heading, it displays that section header with a pin icon (📌).
- Automatic Term Highlighting: Uses <mark> tags to visually highlight search words in titles, abstracts, and match snippets.
- Code-Term Protection: Handles dots and special characters in search words (like .js) correctly, ensuring stable results when searching for programming terminology.
- Minimum Length Threshold: Requires a minimum of 3 characters before initiating a text search to protect performance on large datasets.

## Tag Management & Filtering

- Global Tag Cloud: Dynamically generates a cloud of tags based on the modules available within the currently selected track.
- Visual Tag Suggestions: Scans the tag cloud while you type in the search bar. If a tag partially matches your query, it automatically receives a CSS class (tag-suggestion-highlight) to hint at relevant topics.
- Independent Tag Filtering: Clicking a tag isolates modules containing that tag. The tag filter works together with the search input instead of overwriting it.
- Track Buttons: Fast filters that narrow down the content list based on main discipline/track buttons.
- Toggle Tag Visibility: Supports a checkbox (#tagToggleCheckbox) to hide or display the entire global tag cloud based on user preference.

## Data Ingestion & Parsing

- Asynchronous Parallel Loading: Fetches external .md files in the background using a controlled queue (runWithConcurrency), capped at a maximum of 4 simultaneous requests to protect the server.
- Flexible Ingestion Formats: Accepts module text sources as plain text, URL strings, or structured JSON objects (article.text.text).
- Robust Front-Matter Parser: Scans the top of Markdown files for YAML-like metadata blocks (e.g., --- title: Name ---), extracts them automatically, and converts bracketed lists (like [tag1, tag2]) into proper JavaScript arrays.

## Rendering & Content Injection

- Markdown-to-HTML: Utilizes markdown-it to render rich text with HTML capabilities and automatic link conversion.
- Safe DOM Highlighting: When a module is expanded, it scans the actual text nodes in the DOM tree to highlight search keywords without breaking internal HTML tags or corrupting the markdown structure.
- Dynamic Heading IDs: Generates unique, URL-safe header IDs (slugify) for all headings inside an expanded module to prevent ID collisions between different files.
- Internal Anchor Rewriting: Automatically rewrites standard anchor tags (href="#section") so they point directly to the correct heading within that specific expanded module container.

## UX, Navigation & Routing

- Step-by-Step Learning Paths: Displays a dynamic "Next module" button based on track and order, letting users seamlessly progress through the course content.
- URL Synchronization (Routing): Keeps search strings (?q=), track filters (?track=), tags (?tag=), and the active module (?id=) in sync with the browser address bar. It utilizes popstate so browser forward/backward navigation works perfectly.
- Deep Heading Linking: Supports deep links (e.g., ?id=module-1#introduction), automatically scrolling to the module, expanding it, and smoothly moving down to the targeted section header.
- Share Link Generator: A button inside expanded modules copies a complete direct link to the clipboard and gives instant visual feedback ("Link copied! ✔").
- One-Click Reset: A dedicated reset button completely clears the search field, removes active tag/track filters, and resets the URL parameters in one click.
- Pagination (Load More): Displays up to 10 modules at a time and automatically hides or shows the "Load More" button based on how many modules remain.


## The use of Markdown-it is in this solution based on their provided MIT License for the markdown-it javascript, as follows:

https://github.com/markdown-it/markdown-it?tab=MIT-1-ov-file 

"Copyright (c) 2014 Vitaly Puzrin, Alex Kocharin.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE."


