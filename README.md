# Five Parsecs from Home — Crew Builder

A complete digital crew builder for **Five Parsecs from Home Third Edition**, 
matching the tone, rules, and Crew Log layout of the official rulebook.

---

## Features

- **All species/types** — Baseline Human, all Bots, all Primary Aliens, and all
  Strange Characters with full rules text displayed in-app
- **Full Background, Motivation, and Class tables** — all options from the book
- **Complete weapon list** — all Low-tech, Military, and High-tech weapons with
  correct stats (Range, Shots, Damage, Traits)
- **Ship setup** — all 13 ship types with traits auto-filled
- **Crew-level tracking** — Credits, Story Points, Quest Rumors, Patrons, Rivals
- **Stash management** — shared equipment pool
- **Flavor details** — "We met through" and "Best characterized as" tables
- **Auto-save** to browser storage between sessions
- **Save/Load** as JSON files
- **Export to TXT** — formatted plain-text crew log
- **Export to PDF** — dark-themed layout closely matching the official Crew Log

---

## Quick Start

### Option A — Browser only (TXT export)

1. Open `index.html` in any modern browser
2. Build your crew
3. Click **Export TXT** to download a formatted crew log

### Option B — Full PDF export

Requirements: Python 3.8+ and reportlab

```bash
pip install reportlab
```

Then run the PDF server:

```bash
python pdf_server.py
```

Open `index.html` in your browser. The **Export PDF** button will now generate
a PDF matching the official Crew Log sheet layout.

---

## Crew Creation Quick Reference

### Crew Size
- **Standard Method**: 3 Humans, 2 Human or Primary Alien (choice), 1 Human or Bot (choice)
- **First-timer Method**: 6 Baseline Humans
- **Miniatures Method**: Any combination matching your figures
- **Random Method**: Roll on Crew Type Tables for each slot

### Character Creation Steps
1. Choose species/type
2. (Humans & Primary Aliens) Roll Background, Motivation, and Class tables
3. Apply stat modifiers and resources
4. Name the character; assign as Captain if desired

### Captain
The Captain receives **1 Luck point** and will never leave through random events.
Bots may be Captain but receive no Luck.

### Starting Equipment (whole crew)
- 3 Military Weapon rolls
- 3 Low-tech Weapon rolls
- 1 Gear roll
- 1 Gadget roll
- 1 credit per crew member

---

## File Structure

```
five_parsecs_builder/
├── index.html      — Main crew builder (open in browser)
├── pdf_server.py   — PDF generation server (run with Python)
└── README.md       — This file
```

---

## Notes

This tool is fan-made for personal use. Five Parsecs from Home is 
copyright Ivan Sorenson / Modiphius Entertainment. Permission is 
granted to make copies of the Crew Log for personal use.

The PDF export matches the Crew Log sheet found in Appendix X of the 
rulebook as closely as possible, using the same dark aesthetic and layout.
