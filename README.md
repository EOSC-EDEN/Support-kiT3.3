Github pages show (for now) the content under the branch earlyDemoVersion, not this branch) 

**This code is based on going some steps further in developments from the early mockup of Support kit T3.3 - and gh pages connected to it.** 

**AI have been used in the process to create and check code for the mockup.** 

**The files** are htmls, javascripts, css styling and json for content (the branch also includes a local copy of markdown-it). Should run on any web server as is.

## markdown files in the folder "articles" will end up in index.json, that again is the basis for the full content in gh pages.

## How to contribute with content? 
Write your content in markdown, based on template/ other markdown files in the folder "articles". 

## Note on filtering:

"Track" (or if you like: learning path) is the top level filtering. Next level, under paths, is tags (/keywords).  

## Searching 
A search can both have hits in module titles, tags, module descriptions, as well as module content (the last shown as a small "preview" area, and marked in module content when a module is open). 

## Search Mode (When you TYPE in the search field).

Results are sorted by relevance, and to what degree the search term matches the title etc.:

The code assigns points (scoring) based on where your search term appears:3 points (Highest relevance): If the article title matches the exact word you searched for. 2 points (Medium relevance): If the article title starts with the word you searched for. 1 point (Lowest relevance): If the word is found anywhere inside the title text, inside the abstract (summary), or among the tags.In case of a tie (Equal score):If two articles get the exact same score (for example, if both contain the search term right in the middle of their abstracts), the code falls back on sorting the titles alphabetically to determine which one comes first.

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


