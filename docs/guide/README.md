# Put AI to Work - build notes

`guide.md` is the editable source. `build_pdf.py` turns it into the public PDF.

```sh
python3 -m pip install -r requirements.txt
python3 build_pdf.py
```

The build uses ReportLab and standard PDF fonts, so it does not depend on an author-specific filesystem path or a proprietary font. The PDF contains selectable text, clickable links, page numbers, a cover contents list with page numbers, a PDF outline for navigation, and embedded vector diagrams. The build runs twice: the first pass records where each section starts, and the second pass prints those page numbers on the cover. Render it with Poppler or another PDF viewer and inspect every page after changing copy or layout.

Layout conventions in `build_pdf.py`: each numbered `##` heading becomes a section with a badge and a running header; `### Copyable prompt N - title` becomes a labeled prompt card with selectable text; `>` blockquotes become callouts; ` ```mermaid ` blocks are replaced, in order, by the three vector diagrams; long prompt cards can continue across pages while preserving paragraph breaks; and the bullet list under "References" is set in two columns.
