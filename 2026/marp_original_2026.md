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

  /* ─── Base ─── */
  section {
    font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
    padding: 40px 48px 60px;
    background: #ffffff;
    color: #222222;
    overflow: hidden;
    position: relative;
  }

  /* ─── Footer: library name left ─── */
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

  /* ─── Pagination: date + page number right ─── */
  section::after {
    content: "01.03.2026  |  " attr(data-marpit-pagination);
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

  /* ═══════════════════════════════════════
     SLIDE 1 — Titelfolie
  ═══════════════════════════════════════ */
  section.title {
    padding: 0;
    background: #ffffff;
  }
  /* Dekoratives Hintergrundbild: x=1.69% y=16.52% w=96.1% h=80.39% */
  section.title::before {
    content: '';
    position: absolute;
    left: 1.69%;
    top: 16.52%;
    width: 96.1%;
    height: 80.39%;
    background: url('assets/images/logo_uzh.png') center / 100% 100% no-repeat;
    z-index: 0;
  }
  /* Bibliothek-Logo: x=2.21% y=0.67% w=24.41% */
  .title-logo-lib {
    position: absolute;
    left: 2.21%;
    top: 0.67%;
    width: 24.41%;
    z-index: 2;
  }
  .title-logo-lib img { width: 100%; height: auto; }
  /* UZH-Logo: x=84.74% y=2.75% w=13.04% */
  .title-logo-uzh {
    position: absolute;
    left: 84.74%;
    top: 2.75%;
    width: 13.04%;
    z-index: 2;
  }
  .title-logo-uzh img { width: 100%; height: auto; }
  /* Titeltext: x≈0% y=35.58% w=30.43% */
  .title-text {
    position: absolute;
    left: 4%;
    top: 35%;
    width: 36%;
    z-index: 2;
  }
  .title-text h1 {
    font-size: 1.7em;
    font-weight: 700;
    color: #222222;
    margin: 0 0 10px 0;
    line-height: 1.2;
  }
  .title-text h2 {
    font-size: 1em;
    font-weight: 400;
    color: #444444;
    margin: 0 0 16px 0;
  }
  .title-text .meta {
    font-size: 0.85em;
    color: var(--uzh-gray);
    line-height: 1.5;
  }
  section.title footer { display: none; }
  section.title::after { display: none; }

  /* ═══════════════════════════════════════
     SLIDE 2 — Inhaltsverzeichnis
  ═══════════════════════════════════════ */
  section.toc { padding: 36px 48px 60px; }
  section.toc h1 {
    font-size: 1.7em;
    font-weight: 700;
    color: var(--uzh-blue);
    border-bottom: 2.5px solid var(--uzh-blue);
    padding-bottom: 8px;
    margin: 0 0 28px 0;
  }
  .toc-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px 48px;
  }
  .toc-item h3 {
    font-size: 0.95em;
    font-weight: 700;
    color: var(--uzh-blue);
    margin: 0 0 4px 0;
  }
  .toc-item p {
    font-size: 0.82em;
    color: var(--uzh-gray);
    margin: 0;
    line-height: 1.45;
  }

  /* ═══════════════════════════════════════
     SLIDE 3 — Kapiteltrennfolie
     Band: x=2.16% y=4.62% w=95.63% h=23.1%  #B6D8EB
     Nummer: x=3.69% y=1.3% w=6.58% h=25%
     Titel: x=12.51% y=11.17% w=82.68%
     Bild: x=2.16% y=27.72% w=95.63% h=63.97%
  ═══════════════════════════════════════ */
  section.section-divider {
    background: #ffffff;
    padding: 0;
  }
  /* Dekoratives Hintergrundbild */
  .ch-bg {
    position: absolute;
    left: 2.16%;
    top: 27.72%;
    width: 95.63%;
    height: 63.97%;
    background: url('assets/images/logo_uzh.png') center / 100% 100% no-repeat;
    z-index: 0;
  }
  /* Blauer Band */
  .ch-band {
    position: absolute;
    left: 2.16%;
    top: 4.62%;
    width: 95.63%;
    height: 23.1%;
    background: var(--uzh-band);
    z-index: 1;
  }
  /* Kapitelnummer-Box */
  .ch-num {
    position: absolute;
    left: 3.69%;
    top: 1.3%;
    width: 6.58%;
    height: 26%;
    background: var(--uzh-band);
    z-index: 2;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 4px;
  }
  .ch-num span {
    font-size: 3.5em;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
  }
  /* Kapiteltitel */
  .ch-title {
    position: absolute;
    left: 12.51%;
    top: 0;
    width: 82.68%;
    height: 31.79%; /* 4.62% + 23.1% + some */
    display: flex;
    align-items: center;
    z-index: 2;
  }
  .ch-title h1 {
    font-size: 1.6em;
    font-weight: 700;
    color: #222222;
    margin: 0;
    border: none;
  }
  section.section-divider footer { display: none; }
  section.section-divider::after {
    content: "01.03.2026  |  " attr(data-marpit-pagination);
  }

  /* ═══════════════════════════════════════
     SLIDE 4 — Inhaltsfolie
  ═══════════════════════════════════════ */
  section.content { padding: 36px 48px 60px; }
  section.content h1 {
    font-size: 1.5em;
    font-weight: 700;
    color: var(--uzh-blue);
    border-bottom: 2.5px solid var(--uzh-blue);
    padding-bottom: 6px;
    margin: 0 0 20px 0;
  }
  section.content p {
    font-size: 0.88em;
    line-height: 1.55;
    color: #333;
    margin-bottom: 14px;
  }
  section.content ul { padding-left: 1.2em; margin: 0; }
  section.content li {
    font-size: 0.86em;
    line-height: 1.5;
    color: #333;
    margin-bottom: 4px;
  }
  section.content li li {
    font-size: 0.9em;
    color: var(--uzh-gray);
    list-style-type: circle;
  }

  /* ═══════════════════════════════════════
     SLIDE 5 — Feedback
     Kontakt-Box: x=29.92% y=82.95% w=32.96% h=10.55%
  ═══════════════════════════════════════ */
  section.feedback {
    background: #ffffff;
    color: #222222;
    padding: 0;
  }
  /* Sprechblasen als Bild */
  .fb-symbol {
    position: absolute;
    left: 4%;
    top: 8%;
    width: 92%;
    height: auto;
    z-index: 1;
  }
  /* Kontakt-Box */
  .contact-box {
    position: absolute;
    left: 29.92%;
    top: 82.95%;
    width: 32.96%;
    height: 10.55%;
    border: 2px solid var(--uzh-blue);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 0.88em;
    font-weight: 700;
    color: var(--uzh-blue);
    z-index: 2;
    background: #ffffff;
  }
  .contact-box span {
    font-weight: 400;
    font-size: 0.9em;
    color: var(--uzh-gray);
  }
  section.feedback footer {
    color: var(--uzh-gray);
    border-top-color: var(--uzh-lightgray);
  }
---

<!-- _class: title -->
<!-- _paginate: false -->

<div class="title-logo-lib">
  <img src="assets/images/logo_uzb.png" alt="Bibliothek der Universität Zürich / ZB">
</div>

<div class="title-logo-uzh">
  <img src="assets/images/UZH_logo.png" alt="Universität Zürich">
</div>

<div class="title-text">

# Haupttitel, Textebene 1

## Untertitel, Textebene 2

<div class="meta">
Vorname Name<br>
1. März 2026
</div>

</div>

---

<!-- _class: toc -->

# Inhaltsverzeichnis

<div class="toc-grid">
  <div class="toc-item">
    <h3>Zwischentitel</h3>
    <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit.</p>
  </div>
  <div class="toc-item">
    <h3>Zwischentitel</h3>
    <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit.</p>
  </div>
  <div class="toc-item">
    <h3>Zwischentitel</h3>
    <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit.</p>
  </div>
  <div class="toc-item">
    <h3>Zwischentitel</h3>
    <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit.</p>
  </div>
</div>

---

<!-- _class: section-divider -->
<!-- _paginate: true -->

<div class="ch-bg"></div>
<div class="ch-band"></div>
<div class="ch-num"><span>1</span></div>
<div class="ch-title"><h1>Zwischentitel</h1></div>

---

<!-- _class: content -->

# Folientitel

Text, 16 Pt — Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.

- Aufzählung (Textebene 2) Lorem ipsum dolor sit amet,
- Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et
- Dolore magna aliquyam erat, sed diam voluptua.
  - Aufzählung (Textebene 3) Lorem ipsum
  - Lorem ipsum dolor sit amet, consetetur sadipscing elitr
  - Consetetur sadipscing elitr, sed diam nonumy eirmod tempor

---

<!-- _class: feedback -->
<!-- _paginate: true -->

<div class="fb-symbol">
  <img src="assets/images/feedback_symbol.png" alt="Fragen? Feedback">
</div>

<div class="contact-box">
  <strong>Kontakt</strong>
  <span>nobutake.kamiya@ub.uzh.ch</span>
</div>
