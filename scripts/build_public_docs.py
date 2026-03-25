from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "docs" / "access" / "site"
OUTPUT_ROOTS = [
    REPO_ROOT / "frontend_deploy" / "docs",
    REPO_ROOT / "static" / "docs",
]
SITEMAP_ROOTS = [
    REPO_ROOT / "frontend_deploy" / "sitemap.xml",
    REPO_ROOT / "static" / "sitemap.xml",
]

SECTION_ORDER = [
    "Start Here",
    "Using the Scanner",
    "Understanding the Data",
    "Data Sources",
    "Pipeline",
    "Reference",
    "Appendix",
]

STATUS_LABELS = {
    "stable": "Stable",
    "in-progress": "In Progress",
}

STATUS_CLASS = {
    "stable": "is-stable",
    "in-progress": "is-in-progress",
}

ADMONITION_TITLES = {
    "note": "Note",
    "warning": "Warning",
    "in-progress": "In Progress",
    "methodology": "Methodology",
}


@dataclass(frozen=True)
class TocItem:
    level: int
    heading_id: str
    text: str


@dataclass(frozen=True)
class Page:
    source_path: Path
    title: str
    slug: str
    section: str
    order: int
    summary: str
    status: str
    description: str
    body: str

    @property
    def route(self) -> str:
        return self.slug.strip("/")

    @property
    def output_relative_path(self) -> Path:
        if not self.route:
            return Path("index.html")
        return Path(self.route) / "index.html"

    @property
    def public_url(self) -> str:
        if not self.route:
            return "/docs"
        return f"/docs/{self.route}"

    @property
    def canonical_url(self) -> str:
        return f"https://www.polylab.app{self.public_url}"

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status.title())

    @property
    def status_class(self) -> str:
        return STATUS_CLASS.get(self.status, "is-stable")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build multipage public docs for PolyLab.")
    parser.add_argument("--check", action="store_true", help="Fail if generated output differs from checked-in files.")
    return parser.parse_args()


def read_pages() -> list[Page]:
    pages: list[Page] = []
    for path in sorted(SOURCE_ROOT.rglob("*.md")):
        text = path.read_text("utf-8")
        metadata, body = split_frontmatter(text, path)
        pages.append(
            Page(
                source_path=path,
                title=require_metadata(metadata, "title", path),
                slug=metadata.get("slug", "").strip(),
                section=require_metadata(metadata, "section", path),
                order=int(require_metadata(metadata, "order", path)),
                summary=require_metadata(metadata, "summary", path),
                status=require_metadata(metadata, "status", path),
                description=require_metadata(metadata, "description", path),
                body=body.strip(),
            )
        )
    if not pages:
        raise SystemExit(f"No docs source files found under {SOURCE_ROOT}")
    return sorted(pages, key=lambda page: (SECTION_ORDER.index(page.section), page.order, page.title))


def split_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise SystemExit(f"Missing frontmatter in {path}")
    try:
        _, raw_frontmatter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise SystemExit(f"Invalid frontmatter in {path}") from exc
    metadata: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise SystemExit(f"Invalid frontmatter line in {path}: {line}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, body


def require_metadata(metadata: dict[str, str], key: str, path: Path) -> str:
    value = metadata.get(key)
    if value is None:
        raise SystemExit(f"Missing required frontmatter key '{key}' in {path}")
    return value


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


def escape_inline(value: str) -> str:
    escaped = html.escape(value, quote=True)
    escaped = re.sub(r"`([^`]+)`", lambda match: f"<code>{match.group(1)}</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", lambda match: f"<strong>{match.group(1)}</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        escaped,
    )
    return escaped


def _is_table_line(value: str) -> bool:
    stripped = value.strip()
    return stripped.startswith("|") and stripped.endswith("|") and len(stripped) >= 2


def _is_table_separator(value: str) -> bool:
    stripped = value.strip()
    return bool(re.match(r"^\|[\s:\-|]+\|$", stripped))


def _split_table_row(value: str) -> list[str]:
    stripped = value.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def render_table_block(table_lines: list[str]) -> str:
    if len(table_lines) < 2 or not _is_table_separator(table_lines[1]):
        return "\n".join(f"<p>{escape_inline(line.strip())}</p>" for line in table_lines if line.strip())

    header_cells = _split_table_row(table_lines[0])
    body_rows = [_split_table_row(line) for line in table_lines[2:]]

    parts = ['<div class="docs-table-wrap"><table class="docs-table">', "<thead><tr>"]
    for cell in header_cells:
        parts.append(f"<th>{escape_inline(cell)}</th>")
    parts.append("</tr></thead>")

    if body_rows:
        parts.append("<tbody>")
        for row in body_rows:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{escape_inline(cell)}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")

    parts.append("</table></div>")
    return "".join(parts)


def render_markdown(markdown_text: str) -> tuple[str, list[TocItem]]:
    lines = markdown_text.splitlines()
    html_parts: list[str] = []
    toc: list[TocItem] = []
    paragraph_lines: list[str] = []
    list_stack: list[str] = []
    used_heading_ids: set[str] = set()
    index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            html_parts.append(f"<p>{escape_inline(' '.join(line.strip() for line in paragraph_lines))}</p>")
            paragraph_lines = []

    def close_lists() -> None:
        nonlocal list_stack
        while list_stack:
            html_parts.append(f"</{list_stack.pop()}>")

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_lists()
            index += 1
            continue

        if _is_table_line(stripped):
            flush_paragraph()
            close_lists()
            table_lines: list[str] = []
            while index < len(lines) and _is_table_line(lines[index]):
                table_lines.append(lines[index])
                index += 1
            html_parts.append(render_table_block(table_lines))
            continue

        if stripped.startswith(":::"):
            flush_paragraph()
            close_lists()
            kind = stripped[3:].strip() or "note"
            index += 1
            block_lines: list[str] = []
            while index < len(lines) and lines[index].strip() != ":::":
                block_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                raise SystemExit(f"Unclosed admonition block: {kind}")
            inner_html, _ = render_markdown("\n".join(block_lines))
            html_parts.append(
                f'<div class="docs-admonition docs-admonition-{html.escape(kind, quote=True)}">'
                f'<div class="docs-admonition-title">{ADMONITION_TITLES.get(kind, kind.title())}</div>'
                f"{inner_html}</div>"
            )
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            close_lists()
            language = stripped[3:].strip()
            index += 1
            code_lines: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                raise SystemExit(f"Unclosed code fence for language '{language}'")
            class_attr = f' class="language-{html.escape(language, quote=True)}"' if language else ""
            html_parts.append(f"<pre><code{class_attr}>{html.escape(chr(10).join(code_lines))}</code></pre>")
            index += 1
            continue

        heading_match = re.match(r"^(#{2,3})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            close_lists()
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            heading_id = slugify(text)
            suffix = 2
            while heading_id in used_heading_ids:
                heading_id = f"{heading_id}-{suffix}"
                suffix += 1
            used_heading_ids.add(heading_id)
            toc.append(TocItem(level=level, heading_id=heading_id, text=text))
            html_parts.append(f'<h{level} id="{heading_id}">{escape_inline(text)}</h{level}>')
            index += 1
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            if not list_stack or list_stack[-1] != "ol":
                close_lists()
                list_stack.append("ol")
                html_parts.append("<ol>")
            item_text = re.sub(r"^\d+\.\s+", "", stripped)
            html_parts.append(f"<li>{escape_inline(item_text)}</li>")
            index += 1
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            if not list_stack or list_stack[-1] != "ul":
                close_lists()
                list_stack.append("ul")
                html_parts.append("<ul>")
            html_parts.append(f"<li>{escape_inline(stripped[2:])}</li>")
            index += 1
            continue

        paragraph_lines.append(line)
        index += 1

    flush_paragraph()
    close_lists()
    return "\n".join(html_parts), toc


def render_sidebar(pages: list[Page], current_page: Page) -> str:
    groups: dict[str, list[Page]] = {section: [] for section in SECTION_ORDER}
    for page in pages:
        groups.setdefault(page.section, []).append(page)

    parts = [
        '<aside class="docs-sidebar">',
        '<div class="docs-sidebar-inner">',
        '<p class="docs-sidebar-note">Current implementation docs. Details may change as PolyLab evolves.</p>',
    ]
    for section in SECTION_ORDER:
        items = groups.get(section, [])
        if not items:
            continue
        parts.append(f'<section class="docs-sidebar-group"><div class="docs-sidebar-group-label">{html.escape(section)}</div>')
        for page in items:
            active_class = " is-active" if page == current_page else ""
            parts.append(
                f'<a class="docs-sidebar-link{active_class}" href="{page.public_url}">'
                f'<span>{html.escape(page.title)}</span>'
                "</a>"
            )
        parts.append("</section>")
    parts.append("</div></aside>")
    return "\n".join(parts)


def render_toc(page: Page, toc: list[TocItem]) -> str:
    items = [item for item in toc if item.level in (2, 3)]
    if not items:
        return '<aside class="docs-toc"><div class="docs-toc-inner"><div class="docs-toc-label">On this page</div><p class="docs-toc-empty">No section outline for this page yet.</p></div></aside>'
    parts = [
        '<aside class="docs-toc">',
        '<div class="docs-toc-inner">',
        '<div class="docs-toc-label">On this page</div>',
    ]
    for item in items:
        level_class = " docs-toc-level-3" if item.level == 3 else ""
        parts.append(
            f'<a class="docs-toc-link{level_class}" href="#{html.escape(item.heading_id, quote=True)}">{html.escape(item.text)}</a>'
        )
    parts.append("</div></aside>")
    return "\n".join(parts)


def build_breadcrumb_list(page: Page) -> list[dict[str, object]]:
    crumbs = [
        {"@type": "ListItem", "position": 1, "name": "Docs", "item": "https://www.polylab.app/docs"},
    ]
    if page.route:
        crumbs.append({"@type": "ListItem", "position": 2, "name": page.title, "item": page.canonical_url})
    return crumbs


def faq_schema_for(page: Page) -> dict[str, object] | None:
    if page.route != "faq":
        return None
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Is PolyLab financial advice?",
                "acceptedAnswer": {"@type": "Answer", "text": "No. PolyLab is a research and scanning tool."},
            },
            {
                "@type": "Question",
                "name": "How often is the data updated?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Market snapshots refresh every hour, while Smart Money analysis refreshes every 6 hours.",
                },
            },
            {
                "@type": "Question",
                "name": "Why can PolyLab differ from Polymarket?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "PolyLab works from snapshots and derived metrics, so timing, anomalies, and source cadence can differ from the live Polymarket view.",
                },
            },
        ],
    }


def render_page(page: Page, pages: list[Page], build_label: str) -> str:
    body_html, toc = render_markdown(page.body)
    title = "PolyLab Docs | Documentation" if not page.route else f"PolyLab Docs | {page.title}"
    sidebar_html = render_sidebar(pages, page)
    toc_html = render_toc(page, toc)
    prev_page, next_page = adjacent_pages(pages, page)

    graph: list[dict[str, object]] = [
        {
            "@type": "Organization",
            "name": "PolyLab",
            "url": "https://www.polylab.app",
            "logo": "https://www.polylab.app/assets/polylab-mark.svg",
            "email": "hello@polylab.app",
        },
        {
            "@type": "TechArticle",
            "headline": title,
            "description": page.description,
            "url": page.canonical_url,
            "author": {"@type": "Organization", "name": "PolyLab"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": build_breadcrumb_list(page),
        },
    ]
    faq_graph = faq_schema_for(page)
    if faq_graph is not None:
        graph.append(faq_graph)

    home_banner = ""
    if not page.route:
        home_banner = (
            '<section class="docs-home-banner" aria-label="Documentation introduction notice">'
            "<strong>Implementation-first docs.</strong> "
            "<span>Start here: every page in this section describes the current PolyLab implementation and may change as the product evolves.</span>"
            "</section>"
        )

    article_nav = ['<nav class="docs-article-nav">']
    if prev_page is not None:
        article_nav.append(
            f'<a class="docs-article-nav-link" href="{prev_page.public_url}"><span class="docs-article-nav-label">Previous</span><strong>{html.escape(prev_page.title)}</strong></a>'
        )
    else:
        article_nav.append('<div class="docs-article-nav-link is-empty"></div>')
    if next_page is not None:
        article_nav.append(
            f'<a class="docs-article-nav-link" href="{next_page.public_url}"><span class="docs-article-nav-label">Next</span><strong>{html.escape(next_page.title)}</strong></a>'
        )
    else:
        article_nav.append('<div class="docs-article-nav-link is-empty"></div>')
    article_nav.append("</nav>")

    return f"""<!doctype html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0f111a">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(page.description, quote=True)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{page.canonical_url}">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(page.description, quote=True)}">
  <meta property="og:image" content="https://www.polylab.app/assets/landing-og.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{page.canonical_url}">
  <meta name="twitter:title" content="{html.escape(title, quote=True)}">
  <meta name="twitter:description" content="{html.escape(page.description, quote=True)}">
  <meta name="twitter:image" content="https://www.polylab.app/assets/landing-og.png">
  <link rel="canonical" href="{page.canonical_url}">
  <script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":"))}</script>
  <link rel="icon" href="/assets/polylab-mark.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
{build_css()}
  </style>
</head>
<body data-page-key="docs" data-landing-variant="docs">
  <div class="docs-shell">
    <header class="docs-topbar">
      <div class="docs-topbar-inner">
        <a class="docs-brand" href="/docs">
          <img src="/assets/polylab-mark.svg" alt="PolyLab">
          <span>
            <strong>PolyLab Docs</strong>
            <span>Independent analyzer for Polymarket</span>
          </span>
        </a>
        <nav class="docs-topnav" aria-label="Docs top navigation">
          <a href="/docs">Docs Home</a>
          <a href="/app" data-track-event="cta_click" data-track-placement="docs_topbar" data-track-target="app">Open APP</a>
          <a href="/custom-data">Custom Data</a>
        </nav>
      </div>
    </header>
    <div class="docs-layout">
      {sidebar_html}
      <main class="docs-content">
        <article class="docs-article">
          {home_banner}
          <div class="docs-page-header">
            <div class="docs-page-kicker">{html.escape(page.section)}</div>
            <h1>{html.escape(page.title)}</h1>
            <div class="docs-page-meta">
              <span class="docs-page-updated">Last updated {html.escape(build_label)}</span>
            </div>
            <p class="docs-page-summary">{html.escape(page.summary)}</p>
          </div>
          {body_html}
          {''.join(article_nav)}
        </article>
      </main>
      {toc_html}
    </div>
    <footer class="docs-footer">
      <div>PolyLab Docs</div>
      <div class="docs-footer-links">
        <a href="/docs">Home</a>
        <a href="/docs/faq">Site FAQ</a>
        <button type="button" data-info-trigger="terms">Terms</button>
        <button type="button" data-info-trigger="privacy">Privacy</button>
        <a data-contact-link href="mailto:hello@polylab.app">Contact</a>
      </div>
    </footer>
  </div>
  <div class="info-modal" data-info-modal hidden>
    <div class="info-modal-card">
      <div class="info-modal-head">
        <h3 data-info-modal-title>Terms</h3>
        <button class="info-modal-close" type="button" data-info-close aria-label="Close">x</button>
      </div>
      <div class="info-modal-body" data-info-modal-body></div>
      <div class="info-modal-foot">
        <button class="info-modal-close" type="button" data-info-close>Close</button>
      </div>
    </div>
  </div>
  <script src="/assets/polylab-info-content.js"></script>
  <script src="/assets/polylab-marketing.js"></script>
  <script src="/assets/polylab-tracking.js"></script>
  <script>
    (function () {{
      if (window.initPolyLabMarketingPage) {{
        window.initPolyLabMarketingPage();
      }}
    }}());
  </script>
</body>
</html>
"""


def adjacent_pages(pages: list[Page], current_page: Page) -> tuple[Page | None, Page | None]:
    ordered_pages = pages[:]
    current_index = ordered_pages.index(current_page)
    previous_page = ordered_pages[current_index - 1] if current_index > 0 else None
    next_page = ordered_pages[current_index + 1] if current_index + 1 < len(ordered_pages) else None
    return previous_page, next_page


def build_css() -> str:
    return """
    :root {
      color-scheme: dark;
      --bg: #0b0f17;
      --panel: #131927;
      --panel-soft: rgba(19, 25, 39, 0.78);
      --border: rgba(130, 148, 194, 0.14);
      --border-strong: rgba(130, 148, 194, 0.24);
      --text: #edf2ff;
      --muted: #9da8c6;
      --blue: #4e86ff;
      --green: #00c388;
      --amber: #f2bc58;
      --danger: #ff8e7b;
      --shadow: 0 24px 80px rgba(3, 8, 24, 0.38);
      --sidebar-width: 280px;
      --toc-width: 240px;
      --content-width: 860px;
      --radius: 18px;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: 'IBM Plex Sans', sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(78, 134, 255, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(0, 195, 136, 0.08), transparent 24%),
        linear-gradient(180deg, #080b12 0%, #0b0f17 100%);
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    body.info-modal-open { overflow: hidden; }
    a { color: inherit; text-decoration: none; }
    button, a { -webkit-tap-highlight-color: transparent; }

    .docs-shell { min-height: 100vh; }
    .docs-topbar {
      position: sticky;
      top: 0;
      z-index: 30;
      backdrop-filter: blur(18px);
      background: rgba(8, 11, 18, 0.78);
      border-bottom: 1px solid rgba(130, 148, 194, 0.08);
    }

    .docs-topbar-inner {
      width: min(1480px, calc(100% - 28px));
      margin: 0 auto;
      padding: 14px 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .docs-brand {
      display: inline-flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .docs-brand img {
      width: 32px;
      height: 32px;
    }

    .docs-brand span {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .docs-brand strong,
    .docs-page-kicker,
    .docs-page-header h1,
    .docs-sidebar-group-label,
    .docs-admonition-title {
      font-family: 'Space Grotesk', sans-serif;
      letter-spacing: -0.03em;
    }

    .docs-brand span span {
      color: var(--muted);
      font-size: 0.82rem;
      margin-top: 2px;
    }

    .docs-topnav {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 14px;
      color: var(--muted);
      font-size: 0.93rem;
    }

    .docs-topnav a:hover { color: var(--text); }

    .docs-layout {
      width: min(1480px, calc(100% - 28px));
      margin: 0 auto;
      display: grid;
      grid-template-columns: var(--sidebar-width) minmax(0, var(--content-width)) var(--toc-width);
      gap: 24px;
      padding: 26px 0 56px;
      align-items: start;
    }

    .docs-sidebar,
    .docs-article,
    .docs-toc-inner {
      background: var(--panel-soft);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
    }

    .docs-sidebar {
      position: sticky;
      top: 78px;
      max-height: calc(100vh - 96px);
      overflow: auto;
    }

    .docs-sidebar-inner { padding: 18px 16px; }
    .docs-sidebar-note {
      margin: 0 0 18px;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid rgba(130, 148, 194, 0.16);
      background: rgba(12, 17, 27, 0.48);
      color: var(--muted);
      font-size: 0.84rem;
      line-height: 1.55;
    }

    .docs-sidebar-group + .docs-sidebar-group { margin-top: 18px; }
    .docs-sidebar-group-label {
      color: var(--amber);
      font-size: 0.86rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 8px;
    }

    .docs-sidebar-link {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      padding: 10px 12px;
      border-radius: 12px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.35;
    }

    .docs-sidebar-link:hover,
    .docs-sidebar-link.is-active {
      background: rgba(78, 134, 255, 0.12);
      color: var(--text);
    }

    .docs-content { min-width: 0; }
    .docs-article { padding: 28px 32px; }

    .docs-home-banner {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 22px;
      padding: 15px 18px;
      border-radius: 16px;
      border: 1px solid rgba(242, 188, 88, 0.26);
      background: linear-gradient(135deg, rgba(242, 188, 88, 0.14), rgba(78, 134, 255, 0.08));
      color: #ffe4ae;
      line-height: 1.55;
    }

    .docs-home-banner strong {
      font-family: 'Space Grotesk', sans-serif;
      letter-spacing: -0.02em;
    }

    .docs-page-kicker {
      color: var(--amber);
      font-size: 0.84rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .docs-page-header h1 {
      margin: 10px 0 14px;
      font-size: clamp(2rem, 4vw, 2.9rem);
      line-height: 1.04;
    }

    .docs-page-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-bottom: 14px;
    }

    .docs-page-updated {
      color: var(--muted);
      font-size: 0.84rem;
    }

    .docs-page-summary,
    .docs-article p,
    .docs-article li,
    .docs-article blockquote,
    .docs-toc-empty {
      color: var(--muted);
      line-height: 1.72;
      font-size: 1rem;
    }

    .docs-article h2,
    .docs-article h3 {
      font-family: 'Space Grotesk', sans-serif;
      letter-spacing: -0.03em;
      scroll-margin-top: 96px;
    }

    .docs-article h2 {
      margin: 34px 0 12px;
      font-size: 1.55rem;
    }

    .docs-article h3 {
      margin: 24px 0 10px;
      font-size: 1.16rem;
    }

    .docs-article p { margin: 14px 0; }
    .docs-article ul,
    .docs-article ol {
      margin: 14px 0;
      padding-left: 22px;
    }

    .docs-article li + li { margin-top: 8px; }

    .docs-article code {
      padding: 0.14rem 0.34rem;
      border-radius: 6px;
      background: rgba(78, 134, 255, 0.1);
      color: #e7f0ff;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
      font-size: 0.92em;
    }

    .docs-article pre {
      margin: 18px 0;
      padding: 16px 18px;
      border-radius: 14px;
      overflow: auto;
      background: #0c111b;
      border: 1px solid var(--border);
    }

    .docs-article pre code {
      padding: 0;
      background: transparent;
    }

    .docs-table-wrap {
      margin: 18px 0;
      overflow-x: auto;
      border: 1px solid var(--border);
      border-radius: 16px;
      background: rgba(12, 17, 27, 0.58);
    }

    .docs-table {
      width: 100%;
      border-collapse: collapse;
      min-width: 640px;
    }

    .docs-table th,
    .docs-table td {
      padding: 12px 14px;
      text-align: left;
      vertical-align: top;
      border-bottom: 1px solid rgba(130, 148, 194, 0.12);
      color: var(--muted);
      line-height: 1.5;
      font-size: 0.95rem;
    }

    .docs-table th {
      color: var(--text);
      font-family: 'Space Grotesk', sans-serif;
      letter-spacing: -0.02em;
      background: rgba(78, 134, 255, 0.08);
    }

    .docs-table tr:last-child td {
      border-bottom: 0;
    }

    .docs-admonition {
      margin: 18px 0;
      padding: 18px 18px 4px;
      border-radius: 16px;
      border: 1px solid var(--border-strong);
      background: rgba(19, 25, 39, 0.78);
    }

    .docs-admonition-title {
      margin-bottom: 10px;
      font-size: 1rem;
    }

    .docs-admonition-note { border-color: rgba(78, 134, 255, 0.28); }
    .docs-admonition-warning { border-color: rgba(255, 142, 123, 0.28); }
    .docs-admonition-methodology { border-color: rgba(0, 195, 136, 0.28); }
    .docs-admonition-in-progress { border-color: rgba(242, 188, 88, 0.28); }

    .docs-article-nav {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 34px;
      padding-top: 24px;
      border-top: 1px solid rgba(130, 148, 194, 0.1);
    }

    .docs-article-nav-link {
      display: block;
      min-height: 72px;
      padding: 16px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(12, 17, 27, 0.58);
    }

    .docs-article-nav-link.is-empty {
      visibility: hidden;
    }

    .docs-article-nav-label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .docs-article-nav-link strong { display: block; }

    .docs-toc {
      position: sticky;
      top: 78px;
    }

    .docs-toc-inner {
      padding: 18px 16px;
    }

    .docs-toc-label {
      margin-bottom: 10px;
      color: var(--amber);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.8rem;
      font-weight: 700;
    }

    .docs-toc-link {
      display: block;
      color: var(--muted);
      padding: 7px 0;
      font-size: 0.9rem;
      line-height: 1.35;
    }

    .docs-toc-link:hover { color: var(--text); }
    .docs-toc-level-3 { padding-left: 12px; font-size: 0.84rem; }

    .docs-footer {
      width: min(1480px, calc(100% - 28px));
      margin: 0 auto;
      padding: 0 0 34px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .docs-footer-links {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      justify-content: flex-end;
    }

    .docs-footer-links button {
      appearance: none;
      border: 0;
      background: none;
      padding: 0;
      color: inherit;
      font: inherit;
      cursor: pointer;
    }

    .info-modal {
      position: fixed;
      inset: 0;
      z-index: 40;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(4, 7, 16, 0.72);
      backdrop-filter: blur(16px);
    }

    .info-modal[hidden] { display: none; }

    .info-modal-card {
      width: min(720px, 100%);
      max-height: min(80vh, 720px);
      overflow: auto;
      background: #121726;
      border: 1px solid rgba(130, 148, 194, 0.22);
      border-radius: 24px;
      box-shadow: var(--shadow);
    }

    .info-modal-head,
    .info-modal-foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 22px;
      border-bottom: 1px solid rgba(130, 148, 194, 0.14);
    }

    .info-modal-foot {
      border-top: 1px solid rgba(130, 148, 194, 0.14);
      border-bottom: 0;
      justify-content: flex-end;
    }

    .info-modal-body {
      padding: 22px;
      color: var(--muted);
      line-height: 1.72;
    }

    .info-modal-item {
      display: grid;
      grid-template-columns: 32px minmax(0, 1fr);
      gap: 14px;
      align-items: flex-start;
      padding: 14px 0;
      border-bottom: 1px solid rgba(130, 148, 194, 0.12);
    }

    .info-modal-item:last-child {
      border-bottom: 0;
      padding-bottom: 0;
    }

    .info-modal-index {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 999px;
      background: rgba(78, 134, 255, 0.16);
      border: 1px solid rgba(78, 134, 255, 0.24);
      color: #cfe0ff;
      font-size: 0.82rem;
      font-weight: 600;
    }

    .info-modal-item p { margin: 0; }

    .info-modal-close {
      appearance: none;
      border: 1px solid rgba(130, 148, 194, 0.22);
      background: rgba(18, 22, 34, 0.9);
      color: var(--text);
      border-radius: 999px;
      padding: 10px 16px;
      cursor: pointer;
    }

    @media (max-width: 1220px) {
      .docs-layout {
        grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
      }

      .docs-toc { display: none; }
    }

    @media (max-width: 900px) {
      .docs-layout {
        grid-template-columns: 1fr;
      }

      .docs-sidebar {
        position: static;
        max-height: none;
      }

      .docs-topbar-inner,
      .docs-footer {
        flex-direction: column;
        align-items: flex-start;
      }

      .docs-footer-links {
        justify-content: flex-start;
      }
    }

    @media (max-width: 720px) {
      .docs-article { padding: 22px 20px; }
      .docs-topnav { gap: 10px; font-size: 0.88rem; }
      .docs-page-header h1 { font-size: 2rem; }
      .docs-article-nav { grid-template-columns: 1fr; }
    }
"""


def render_outputs(pages: list[Page]) -> dict[Path, str]:
    build_label = "2026-03-10"
    rendered: dict[Path, str] = {}
    for page in pages:
        rendered[page.output_relative_path] = render_page(page, pages, build_label)
    return rendered


def sitemap_content(pages: list[Page]) -> str:
    urls = [
        "https://www.polylab.app/",
        "https://www.polylab.app/docs",
    ]
    for page in pages:
        if page.route:
            urls.append(f"https://www.polylab.app/docs/{page.route}")
    urls.append("https://www.polylab.app/custom-data")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def write_rendered_outputs(rendered: dict[Path, str], pages: list[Page]) -> None:
    for output_root in OUTPUT_ROOTS:
        if output_root.exists():
            shutil.rmtree(output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        for relative_path, content in rendered.items():
            target = output_root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    sitemap = sitemap_content(pages)
    for target in SITEMAP_ROOTS:
        target.write_text(sitemap, encoding="utf-8")


def check_rendered_outputs(rendered: dict[Path, str], pages: list[Page]) -> int:
    mismatches: list[str] = []
    for output_root in OUTPUT_ROOTS:
        for relative_path, content in rendered.items():
            target = output_root / relative_path
            if not target.exists():
                mismatches.append(f"Missing generated file: {target}")
                continue
            if target.read_text("utf-8") != content:
                mismatches.append(f"Out-of-date generated file: {target}")
    sitemap = sitemap_content(pages)
    for target in SITEMAP_ROOTS:
        if not target.exists():
            mismatches.append(f"Missing sitemap file: {target}")
            continue
        if target.read_text("utf-8") != sitemap:
            mismatches.append(f"Out-of-date sitemap file: {target}")
    if mismatches:
        sys.stderr.write("\n".join(mismatches) + "\n")
        return 1
    return 0


def main() -> int:
    args = parse_args()
    pages = read_pages()
    rendered = render_outputs(pages)
    if args.check:
        return check_rendered_outputs(rendered, pages)
    write_rendered_outputs(rendered, pages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
