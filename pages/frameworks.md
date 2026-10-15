---
title: Frameworks
description: How the support-kit maps to certification, preservation and FAIR frameworks.
page_id: frameworks
toc: false
---

The kit connects to existing frameworks in two ways. **Modules cite them directly**, and **WP1 maps each Core Preservation Process** to CoreTrustSeal, the nestor Seal, ISO 16363, OAIS and PREMIS. Both are listed below, so you can see what the kit adds on top of WP1.

{% for fw in site.data.frameworks %}
### {{ fw.label }}
{%- assign citing = site.pages | where_exp: "p", "p.satisfies != nil" %}
{%- capture rows -%}
{%- for p in citing -%}{%- assign hits = p.satisfies | where: "framework", fw.id -%}{%- if hits.size > 0 -%}{%- assign codes = hits | map: "code" | compact | join: ", " -%}
<li><a href="{{ p.url | relative_url }}">{{ p.title }}</a>{% if codes != "" %} — {{ codes }}{% endif %}</li>
{%- endif -%}{%- endfor -%}
{%- endcapture %}
{%- if fw.wp1 %}{%- assign mapped = 0 %}{%- for c in site.data.cpps.cpps %}{%- assign m = c.mappings | where: "framework", fw.wp1 %}{%- if m.size > 0 %}{%- assign mapped = mapped | plus: 1 %}{%- endif %}{%- endfor %}{% endif %}
<p class="small text-secondary"><a href="{{ fw.url }}">{{ fw.url }}</a>{% if fw.wp1 %} · WP1 maps {{ mapped }} of 30 CPPs to it{% endif %}</p>
{%- if rows != "" %}
<p class="xwalk-source">Cited by modules</p>
<ul>{{ rows }}</ul>
{%- else %}
<p class="text-secondary">No module cites it directly yet.</p>
{%- endif %}
{% endfor %}
