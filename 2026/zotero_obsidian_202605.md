---
marp: true
theme: default
size: 16:9
paginate: true
html: true
footer: "Universitätsbibliothek und Zentralbibliothek Zürich"
style: |
  @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap');

  :root {
    --uzh-blue:      #0028A5;
    --uzh-cyan:      #4AC9E3;
    --uzh-band:      #B6D8EB;
    --uzh-gray:      #666666;
    --uzh-lightgray: #D7D7D7;
    font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
  }

  section {
    font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
    padding: 40px 48px 60px;
    background: #ffffff;
    color: #222222;
    overflow: hidden;
    position: relative;
  }

  footer {
    position: absolute;
    bottom: 14px;
    left: 2.21%;
    width: 60%;
    font-size: 0.62em;
    font-weight: 700;
    color: var(--uzh-gray);
    border-top: 1px solid var(--uzh-lightgray);
    padding-top: 3px;
  }

  section::after {
    content: "Mai 2026  |  " attr(data-marpit-pagination);
    font-size: 0.62em;
    color: var(--uzh-gray);
    position: absolute;
    bottom: 14px;
    right: 2%;
    border-top: 1px solid var(--uzh-lightgray);
    padding-top: 3px;
    width: 20%;
    text-align: right;
  }

  /* ─── SLIDE 1: Titelfolie ─── */
  section.title {
    padding: 0;
    background: #ffffff;
  }
  section.title::before {
    content: '';
    position: absolute;
    left: 1.69%; top: 16.52%;
    width: 96.1%; height: 80.39%;
    background: url('../assets/images/logo_uzh.png') center / 100% 100% no-repeat;
    z-index: 0;
  }
  .title-logo-lib {
    position: absolute;
    left: 2.21%; top: 0.67%; width: 24.41%; z-index: 2;
  }
  .title-logo-lib img { width: 100%; height: auto; }
  .title-logo-uzh {
    position: absolute;
    left: 84.74%; top: 2.75%; width: 13.04%; z-index: 2;
  }
  .title-logo-uzh img { width: 100%; height: auto; }
  .title-text {
    position: absolute;
    left: 4%; top: 33%; width: 40%; z-index: 2;
  }
  .title-text h1 {
    font-size: 1.6em; font-weight: 700; color: #222222;
    margin: 0 0 10px 0; line-height: 1.2;
  }
  .title-text h2 {
    font-size: 0.95em; font-weight: 400; color: #444444;
    margin: 0 0 16px 0;
  }
  .title-text .meta { font-size: 0.82em; color: var(--uzh-gray); line-height: 1.6; }
  section.title footer { display: none; }
  section.title::after { display: none; }

  /* ─── SLIDE 2: Inhaltsverzeichnis ─── */
  section.toc { padding: 36px 48px 60px; }
  section.toc h1 {
    font-size: 1.7em; font-weight: 700; color: var(--uzh-blue);
    border-bottom: 2.5px solid var(--uzh-blue);
    padding-bottom: 8px; margin: 0 0 28px 0;
  }
  .toc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 48px; }
  .toc-item h3 {
    font-size: 0.95em; font-weight: 700; color: var(--uzh-blue); margin: 0 0 4px 0;
  }
  .toc-item p { font-size: 0.82em; color: var(--uzh-gray); margin: 0; line-height: 1.45; }

  /* ─── SLIDE 3 / Kapiteltrennfolien ─── */
  section.section-divider { background: #ffffff; padding: 0; }
  .ch-bg {
    position: absolute; left: 2.16%; top: 27.72%;
    width: 95.63%; height: 63.97%;
    background: url('../assets/images/logo_uzh.png') center / 100% 100% no-repeat;
    z-index: 0;
  }
  .ch-band {
    position: absolute; left: 2.16%; top: 4.62%;
    width: 95.63%; height: 23.1%;
    background: var(--uzh-band); z-index: 1;
  }
  .ch-num {
    position: absolute; left: 3.69%; top: 1.3%;
    width: 6.58%; height: 26%;
    background: var(--uzh-band); z-index: 2;
    display: flex; align-items: flex-end; justify-content: center; padding-bottom: 4px;
  }
  .ch-num span { font-size: 3.5em; font-weight: 900; color: #ffffff; line-height: 1; }
  .ch-title {
    position: absolute; left: 12.51%; top: 0;
    width: 82.68%; height: 31.79%;
    display: flex; align-items: center; z-index: 2;
  }
  .ch-title h1 { font-size: 1.6em; font-weight: 700; color: #222222; margin: 0; border: none; }
  section.section-divider footer { display: none; }
  section.section-divider::after {
    content: "Mai 2026  |  " attr(data-marpit-pagination);
  }

  /* ─── Content slides ─── */
  section.content { padding: 36px 48px 60px; }
  section.content h1 {
    font-size: 1.45em; font-weight: 700; color: var(--uzh-blue);
    border-bottom: 2.5px solid var(--uzh-blue);
    padding-bottom: 6px; margin: 0 0 18px 0;
  }
  section.content h2 {
    font-size: 1em; font-weight: 700; color: var(--uzh-blue);
    margin: 16px 0 6px 0;
  }
  section.content p { font-size: 0.86em; line-height: 1.55; color: #333; margin-bottom: 10px; }
  section.content ul { padding-left: 1.2em; margin: 0 0 8px 0; }
  section.content li { font-size: 0.84em; line-height: 1.5; color: #333; margin-bottom: 4px; }
  section.content li li { font-size: 0.9em; color: var(--uzh-gray); list-style-type: circle; }
  section.content ol { padding-left: 1.4em; margin: 0 0 8px 0; }
  section.content ol li { font-size: 0.84em; line-height: 1.5; color: #333; margin-bottom: 6px; }

  /* Zwei-Spalten-Layout */
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px 40px;
    margin-top: 4px;
  }
  .col-box {
    background: #f4f7ff;
    border-left: 4px solid var(--uzh-blue);
    padding: 14px 16px;
    border-radius: 0 4px 4px 0;
  }
  .col-box h3 {
    font-size: 0.9em; font-weight: 700;
    color: var(--uzh-blue); margin: 0 0 8px 0;
  }
  .col-box ul { padding-left: 1.1em; margin: 0; }
  .col-box li { font-size: 0.82em; line-height: 1.5; color: #333; margin-bottom: 4px; }

  /* Hinweis-Box */
  .hint-box {
    background: #fff8e1;
    border-left: 4px solid var(--uzh-yellow, #FFC845);
    padding: 10px 14px;
    border-radius: 0 4px 4px 0;
    font-size: 0.82em;
    color: #555;
    margin-top: 16px;
  }

  /* Schritt-Box */
  .step {
    display: flex;
    gap: 14px;
    margin-bottom: 12px;
    align-items: flex-start;
  }
  .step-num {
    min-width: 28px; height: 28px;
    background: var(--uzh-blue);
    color: #fff;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85em; font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .step-text { font-size: 0.84em; line-height: 1.5; color: #333; }
  .step-text strong { color: #111; }

  /* ─── SLIDE 12: Feedback ─── */
  section.feedback { background: #ffffff; color: #222222; padding: 0; }
  .fb-symbol { position: absolute; left: 4%; top: 8%; width: 92%; height: auto; z-index: 1; }
  .contact-box {
    position: absolute; left: 29.92%; top: 82.95%; width: 32.96%; height: 10.55%;
    border: 2px solid var(--uzh-blue);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-size: 0.88em; font-weight: 700; color: var(--uzh-blue);
    z-index: 2; background: #ffffff;
  }
  .contact-box span { font-weight: 400; font-size: 0.9em; color: var(--uzh-gray); }
  section.feedback footer { color: var(--uzh-gray); border-top-color: var(--uzh-lightgray); }
---

<!-- _class: title -->
<!-- _paginate: false -->

<div class="title-logo-lib">
  <img src="../assets/images/logo_uzb.png" alt="Bibliothek der Universität Zürich / ZB">
</div>

<div class="title-logo-uzh">
  <img src="../assets/images/UZH_logo.png" alt="Universität Zürich">
</div>

<div class="title-text">

# Zotero und Obsidian verbinden

## Highlights & Notizen nahtlos nutzbar machen

<div class="meta">
Nobutake Kamiya<br>
Caffee Lecture · Mai 2026
</div>

</div>

---

<!-- _class: toc -->

# Inhaltsverzeichnis

<div class="toc-grid">
  <div class="toc-item">
    <h3>1 · Voraussetzungen</h3>
    <p>Plugins für Zotero und Obsidian installieren und konfigurieren.</p>
  </div>
  <div class="toc-item">
    <h3>2 · Schritte in Zotero</h3>
    <p>Texte hervorheben, kommentieren und eine Notiz erstellen.</p>
  </div>
  <div class="toc-item">
    <h3>3 · Setup in Obsidian</h3>
    <p>Citations-Plugin und Zotero Integration einrichten.</p>
  </div>
  <div class="toc-item">
    <h3>4 · Workflow in Obsidian</h3>
    <p>Literaturnotizen anlegen, importieren und aufteilen.</p>
  </div>
</div>

---

<!-- _class: section-divider -->
<!-- _paginate: true -->

<div class="ch-bg"></div>
<div class="ch-band"></div>
<div class="ch-num"><span>1</span></div>
<div class="ch-title"><h1>Voraussetzungen</h1></div>

---

<!-- _class: content -->

# Benötigte Plugins

<div class="two-col">
  <div class="col-box">
    <h3>Für Zotero</h3>
    <ul>
      <li><strong>BetterBibTex</strong><br>
        Exportiert die Bibliothek als <code>.bib</code>-Datei und hält sie automatisch aktuell.</li>
    </ul>
  </div>
  <div class="col-box">
    <h3>Für Obsidian</h3>
    <ul>
      <li><strong>Citations</strong> – Literaturnotizen aus der BibTex-Datenbank anlegen</li>
      <li><strong>Zotero Integration</strong> – Anmerkungen mit Hyperlinks importieren</li>
      <li><strong>Note Refactor</strong> – Notizen in einzelne Dateien aufteilen</li>
    </ul>
  </div>
</div>

<div class="hint-box">
  💡 <strong>Wichtig:</strong> In Zotero die Export-Datenbank im BibTeX-Format mit <em>„Keep updated"</em> aktuell halten.
  Im Citations-Plugin muss der Pfad zur exportierten Datei hinterlegt sein.
</div>

---

<!-- _class: section-divider -->
<!-- _paginate: true -->

<div class="ch-bg"></div>
<div class="ch-band"></div>
<div class="ch-num"><span>2</span></div>
<div class="ch-title"><h1>Schritte in Zotero</h1></div>

---

<!-- _class: content -->

# Lesen, Markieren und Notizen erstellen

<div class="step">
  <div class="step-num">1</div>
  <div class="step-text">
    <strong>Volltexte hervorheben und Anmerkungen hinzufügen</strong><br>
    Relevante Textpassagen markieren und Kommentare ergänzen – auch bequem auf dem iPad.
    Anmerkungen können diktiert werden, um Gedanken direkt in eigenen Worten zu verbalisieren.
  </div>
</div>

<div class="step">
  <div class="step-num">2</div>
  <div class="step-text">
    <strong>Notiz aus Anmerkungen erstellen</strong><br>
    In Zotero die Funktion <em>„Notiz aus Anmerkungen hinzufügen"</em> verwenden.
    Dadurch werden alle Anmerkungen in einer übersichtlichen Notiz zusammengestellt –
    mit Hyperlinks zu den jeweils markierten Passagen in den Volltext-PDFs.
  </div>
</div>

---

<!-- _class: section-divider -->
<!-- _paginate: true -->

<div class="ch-bg"></div>
<div class="ch-band"></div>
<div class="ch-num"><span>3</span></div>
<div class="ch-title"><h1>Setup in Obsidian</h1></div>

---

<!-- _class: content -->

# Citations-Plugin einrichten

## Installation
- Über die Obsidian-Einstellungen → *Third-party plugins* → Citations (erfordert Obsidian ≥ 0.9.20)

## Bibliothek aus Zotero exportieren
- In Zotero: **File → Export library …**
- Format: **Better BibLaTeX** wählen
- Option **„Keep updated"** aktivieren ✓ *(empfohlen – aktualisiert die Datei automatisch)*

## Pfad in Obsidian hinterlegen
- Obsidian-Einstellungen → Citations-Tab
- Pfad zur exportierten `.bib`-Datei eintragen
- *Literature note folder* festlegen (z.&nbsp;B. `Readings`)

---

<!-- _class: content -->

# Zotero Integration

## Installation
- Über die Obsidian-Einstellungen → *Third-party plugins* → Zotero Integration

## Konfiguration
- Für bestehende Obsidian-Sites ist **keine weitere Konfiguration nötig**
- Das Plugin ermöglicht den Import von Anmerkungen **mit direkten Hyperlinks** zurück in die Zotero-PDFs

<div class="hint-box">
  ℹ️ Das Citations-Plugin allein kann keine Hyperlinks zu den Textstellen in Zotero-Volltexten erzeugen –
  dafür wird das <strong>Zotero Integration Plugin</strong> benötigt.
</div>

---

<!-- _class: section-divider -->
<!-- _paginate: true -->

<div class="ch-bg"></div>
<div class="ch-band"></div>
<div class="ch-num"><span>4</span></div>
<div class="ch-title"><h1>Workflow in Obsidian</h1></div>

---

<!-- _class: content -->

# Von der Literaturnotiz zur Inhaltsnotiz

<div class="step">
  <div class="step-num">1</div>
  <div class="step-text">
    <strong>Literaturnotiz mit Citations-Plugin anlegen</strong><br>
    Template anpassen (DOI, Schlagworte, Autor:innen als Hyperlink).
    Dateiname = BibTex Citekey, i.d.R. nach Schema <code>@AutorJahrTitel</code>
  </div>
</div>
<div class="step">
  <div class="step-num">2</div>
  <div class="step-text">
    <strong>Anmerkungen importieren (Zotero Integration)</strong><br>
    Die importierten Anmerkungen enthalten Hyperlinks zu den entsprechenden Textstellen in Zotero-Volltexten.
  </div>
</div>
<div class="step">
  <div class="step-num">3</div>
  <div class="step-text">
    <strong>Überschriften für Anmerkungen vergeben</strong><br>
    Aussagekräftige Titel für einzelne Highlights, damit sie später leichter auffindbar sind.
  </div>
</div>
<div class="step">
  <div class="step-num">4</div>
  <div class="step-text">
    <strong>Notizen aufteilen mit Note Refactor</strong><br>
    <em>„Extract selection to new note – first line as file name"</em> <kbd>⇧⌘R</kbd> —
    jede Überschrift wird zum Titel einer neuen Inhaltsnotiz; Links bleiben in der Literaturnotiz.
  </div>
</div>

---

<!-- _class: feedback -->
<!-- _paginate: true -->

<div class="fb-symbol">
  <img src="../assets/images/feedback_symbol.png" alt="Fragen? Feedback">
</div>

<div class="contact-box">
  <strong>Kontakt</strong>
  <span>nobutake.kamiya@ub.uzh.ch</span>
</div>
