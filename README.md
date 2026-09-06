An early mockup of Support kit T3.3 - in the branch orphant. AI have been used to create and check code for the mock-up.

html,js,css and json (includes also markdown-it). should run on any web server as is. 

### index.json is the basis for the full content. 
encoding can be html, plain or markdown in the json text field, but only markdown is used at this point in time.

## how to contribute with content? 
write your content in markdown (any editor can be used as of now). Copy-paste between markdown editor and editor.html provided here.

### Using editor.html can be used to suggest changes in proper json formatting.
The whole index.json will be loaded as defaut starting point, create your suggestion and export -  should keep the json file called index.json in a proper state.

### Note on filtering, sorting and order:

"Track" (or if you like: learning path) is the top level filtering. Tags are next level for filtering (filtered by tracks), then search. Modules are filtered by tracks, tags and search. 

A search can both have hits in module titles, tags, module descriptions, as well as module content (the last shown as a small "preview" area). 

### 1. Default Mode (When the search field is EMPTY)

Within each track, the modules are sorted according to the numerical order field (e.g., 1, 2, 3). This ensures that the course material and modules are arranged in a pedagogical sequence (e.g., Introduction to Step 1 to Step 2) - long reads are possible.

This logic is also what allows your code to automatically find the "Next Module" by looking for an article in the same track with an order + 1 value.


### 2. Search Mode (When you TYPE in the search field).

As soon as you type a word into the search field, the default mode turns off completely. The learning path/track and the order numbers are entirely ignored. Instead, results are sorted by relevance (how well the search term matches the title):

The code assigns points (scoring) based on where your search term appears:3 points (Highest relevance): If the article title matches the exact word you searched for.2 points (Medium relevance): If the article title starts with the word you searched for.1 point (Lowest relevance): If the word is found anywhere inside the title text, inside the abstract (summary), or among the tags.In case of a tie (Equal score):If two articles get the exact same score (for example, if both contain the search term right in the middle of their abstracts), the code falls back on sorting the titles alphabetically (titleA.localeCompare(titleB)) to determine which one comes first.

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


