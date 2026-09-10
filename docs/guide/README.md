# Put AI to Work - build notes

`guide.md` is the editable source. `build_pdf.py` turns it into the public PDF.

```sh
python3 -m pip install -r requirements.txt
python3 build_pdf.py
```

The build uses ReportLab and standard PDF fonts, so it does not depend on an author-specific filesystem path or a proprietary font. The PDF contains selectable text, clickable links, page numbers, and embedded vector diagrams. Render it with Poppler or another PDF viewer and inspect every page after changing copy or layout.
