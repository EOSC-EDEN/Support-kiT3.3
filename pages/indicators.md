---
title: Re-use fitness indicators
description: WP1's 74 indicators of whether research data is fit to be re-used, in three pillars, and the modules that address them.
page_id: indicators
toc: false
---
{%- assign ind = site.data.indicators %}
{%- assign total = 0 %}{% for p in ind.pillars %}{% assign total = total | plus: p.count %}{% endfor %}

[Core Preservation Processes](cpps) describe what a repository does. **Re-use fitness indicators** describe what makes the data itself fit for someone else to use. EOSC EDEN WP1 defined {{ total }} indicators in three pillars, derived from ISO/IEC 25012 (data quality) and refined with institutional policies, standards and expert input.

<div class="ind-pillars">
{%- for p in ind.pillars %}
{%- assign listed = ind.indicators | where: "pillar", p.label %}
  <a class="ind-pillar" href="#{{ p.id | downcase }}">
    <span class="ind-pillar-head"><i class="{{ p.icon }}" aria-hidden="true"></i><span class="ind-code">{{ p.id }}</span></span>
    <b>{{ p.label }}</b>
    <span class="ind-about">{{ p.about }}</span>
    <span class="ind-count"><strong>{{ p.count }}</strong> indicators</span>
  </a>
{%- endfor %}
</div>

## How the kit uses them

Modules will be anchored to indicators the same way they are anchored to processes: a module names the one to three indicators it mainly helps with, and any others it touches. Each indicator gets its own page listing those modules, so you can go from "our metadata is hard to understand" to the guidance that fixes it.

This pairs naturally with the processes. Researchers preparing a deposit mostly act on content and metadata quality; repository managers checking incoming files act on technical data quality through processes such as [File Format Validation](cpp_010).

{%- for p in ind.pillars %}
{%- assign listed = ind.indicators | where: "pillar", p.label %}

<h2 id="{{ p.id | downcase }}">{{ p.label }} <span class="ind-h-count">{{ p.count }}</span></h2>
{%- if listed.size > 0 %}
<ul class="mod-list">
  {%- for i in listed %}
  <li><a href="{{ i.id | downcase | replace: '-', '_' | prepend: '/ind_' | relative_url }}"><span class="cpp-id">{{ i.id }}</span> {{ i.label }}</a></li>
  {%- endfor %}
</ul>
{%- else %}
<p class="ind-empty">The {{ p.count }} {{ p.label | downcase }} indicators will be listed here, each with its own page, once WP1's indicator data is imported into the kit.</p>
{%- endif %}
{%- endfor %}

## About the metrics

Alongside the indicators, the report collects **{{ ind.metrics.candidate }} candidate metrics** ({{ ind.metrics.generic }} generic, {{ ind.metrics.data_specific }} specific to a data type), drawn from policies and certification documents. They are candidates for further validation: EOSC EDEN does not endorse them as requirements, and the kit will show them as examples, not as rules.

<p class="text-secondary small">Source: {{ ind.source.title }}, <a href="https://doi.org/{{ ind.source.doi }}">doi:{{ ind.source.doi }}</a>, {{ ind.source.version }}. {{ ind.source.license }}. Pillar summaries above are the kit's own wording.</p>
