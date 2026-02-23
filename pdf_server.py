"""
Five Parsecs from Home — Crew Log PDF Generator
================================================
Run this server alongside the HTML crew builder.
It receives crew data as JSON and returns a PDF
matching the layout of the official crew log sheet.

Usage:
    python pdf_server.py

The HTML builder will POST to http://localhost:5678/pdf
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import io
import sys

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("ERROR: reportlab not installed. Run: pip install reportlab")
    sys.exit(1)


# ── Colour palette matching the rulebook's dark aesthetic ─────────────────────
BG        = HexColor('#1a1a2e')
SURFACE   = HexColor('#16213e')
GOLD      = HexColor('#c9a227')
GOLD_LIGHT= HexColor('#e8c06a')
BORDER    = HexColor('#2a3045')
TEXT      = HexColor('#d0d4e0')
TEXT_DIM  = HexColor('#7a8098')
TEXT_DARK = HexColor('#0d0f14')
RED_DARK  = HexColor('#7a1a10')


def make_crew_log_pdf(crew: dict) -> bytes:
    buf = io.BytesIO()
    w, h = A4
    c = rl_canvas.Canvas(buf, pagesize=A4)
    w, h = A4  # 595.27 x 841.89 pts

    def draw_page_1():
        # Full page dark background
        c.setFillColor(BG)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # Top header bar
        c.setFillColor(SURFACE)
        c.rect(0, h - 50*mm, w, 50*mm, fill=1, stroke=0)

        c.setStrokeColor(GOLD)
        c.setLineWidth(1.5)
        c.line(0, h - 50*mm, w, h - 50*mm)

        # Title
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(12*mm, h - 22*mm, "FIVE PARSECS FROM HOME")
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_DIM)
        c.drawString(12*mm, h - 29*mm, "CREW LOG — THIRD EDITION")

        # Crew name / story points header
        name = crew.get('name', '') or '—'
        credits_val = crew.get('credits', 0)
        story = crew.get('storyPoints', 0)
        rumors = crew.get('questRumors', 0)
        patrons = crew.get('patrons', 0)
        rivals = crew.get('rivals', 0)

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(TEXT)
        c.drawString(12*mm, h - 40*mm, name)

        # Right side header stats
        right_x = w - 80*mm
        def header_stat(label, val, x, y):
            c.setFont("Helvetica", 6)
            c.setFillColor(TEXT_DIM)
            c.drawString(x, y + 5, label.upper())
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(GOLD)
            c.drawString(x, y - 3, str(val))

        header_stat("Credits",      credits_val, right_x,         h - 24*mm)
        header_stat("Story Points", story,       right_x + 22*mm, h - 24*mm)
        header_stat("Quest Rumors", rumors,      right_x,         h - 38*mm)
        header_stat("Patrons",      patrons,     right_x + 22*mm, h - 38*mm)
        header_stat("Rivals",       rivals,      right_x + 44*mm, h - 38*mm)

        # ── Two-column layout ────────────────────────────────────────────
        col1_x = 12*mm
        col2_x = w/2 + 3*mm
        col_w  = w/2 - 15*mm
        y_start = h - 58*mm

        # ── STASH / SHIP section ─────────────────────────────────────────
        ship = crew.get('ship', {})
        stash = crew.get('stash', '') or ''

        # Ship box (right column, top)
        draw_box(c, col2_x, y_start - 42*mm, col_w, 42*mm, "SHIP DETAILS")
        sy = y_start - 12*mm
        ship_fields = [
            ("Ship Name", ship.get('name','') or '—'),
            ("Type",      ship.get('type','') or '—'),
            ("Hull Points", str(ship.get('hull','') or '—')),
            ("Debt",      str(ship.get('debt', 0)) + " credits"),
            ("Trait",     ship.get('trait','') or 'None'),
            ("Upgrades",  ship.get('upgrades','') or 'None'),
        ]
        for label, val in ship_fields:
            c.setFont("Helvetica", 6)
            c.setFillColor(TEXT_DIM)
            c.drawString(col2_x + 2*mm, sy + 4, label.upper())
            c.setFont("Helvetica", 9)
            c.setFillColor(TEXT)
            c.drawString(col2_x + 2*mm, sy - 4, val[:45])
            sy -= 6*mm

        # Stash box (left column, top area)
        draw_box(c, col1_x, y_start - 42*mm, col_w, 42*mm, "STASH & SHARED EQUIPMENT")
        stash_lines = (stash or '(empty)').split('\n')[:6]
        sy = y_start - 12*mm
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT)
        for line in stash_lines:
            c.drawString(col1_x + 2*mm, sy, line[:50])
            sy -= 5*mm

        # Notes / Flavor
        met   = crew.get('met','') or ''
        char  = crew.get('characterizedAs','') or ''
        notes = crew.get('notes','') or ''
        draw_box(c, col1_x, y_start - 75*mm, w - 24*mm, 31*mm, "CREW NOTES & FLAVOR")
        ny = y_start - 52*mm
        if met:
            c.setFont("Helvetica-Oblique", 7)
            c.setFillColor(TEXT_DIM)
            c.drawString(col1_x + 2*mm, ny, "We met through:")
            c.setFont("Helvetica", 8)
            c.setFillColor(TEXT)
            c.drawString(col1_x + 35*mm, ny, met)
            ny -= 5*mm
        if char:
            c.setFont("Helvetica-Oblique", 7)
            c.setFillColor(TEXT_DIM)
            c.drawString(col1_x + 2*mm, ny, "Best characterized as:")
            c.setFont("Helvetica", 8)
            c.setFillColor(TEXT)
            c.drawString(col1_x + 42*mm, ny, char)
            ny -= 5*mm
        if notes:
            c.setFont("Helvetica", 8)
            c.setFillColor(TEXT)
            for line in notes.split('\n')[:2]:
                c.drawString(col1_x + 2*mm, ny, line[:90])
                ny -= 5*mm

        # ── CREW MEMBERS ─────────────────────────────────────────────────
        members = crew.get('members', [])
        captain = next((m for m in members if m.get('isCapitain')), None)
        others  = [m for m in members if not m.get('isCapitain')]

        section_y = y_start - 80*mm

        # Section heading
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(col1_x, section_y + 2, "CREW MEMBERS")
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(col1_x, section_y, w - 12*mm, section_y)

        section_y -= 4*mm

        # Captain first, then pairs
        all_members = ([captain] if captain else []) + others

        for i, m in enumerate(all_members):
            if m is None:
                continue
            # Two characters per row
            col_offset = col1_x if (i % 2 == 0) else col2_x
            # new row?
            if i % 2 == 0 and i > 0:
                section_y -= 60*mm  # height of each member block

            if section_y < 20*mm:
                c.showPage()
                draw_page_bg(c, w, h)
                section_y = h - 20*mm

            draw_member_block(c, m, col_offset, section_y, col_w)

        # Page footer
        draw_footer(c, w)
        c.showPage()

    def draw_page_bg(c, w, h):
        c.setFillColor(BG)
        c.rect(0, 0, w, h, fill=1, stroke=0)

    def draw_box(c, x, y, bw, bh, title=''):
        c.setFillColor(SURFACE)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.rect(x, y, bw, bh, fill=1, stroke=1)
        if title:
            c.setFillColor(BORDER)
            c.rect(x, y + bh - 5*mm, bw, 5*mm, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 6)
            c.setFillColor(GOLD)
            c.drawString(x + 2*mm, y + bh - 3.5*mm, title)

    def draw_member_block(c, m, x, y, bw):
        bh = 56*mm
        is_cap = m.get('isCapitain', False)
        border_col = GOLD if is_cap else BORDER

        c.setFillColor(SURFACE)
        c.setStrokeColor(border_col)
        c.setLineWidth(1 if is_cap else 0.5)
        c.rect(x, y - bh, bw, bh, fill=1, stroke=1)

        # Title bar
        c.setFillColor(GOLD if is_cap else BORDER)
        c.rect(x, y - 6*mm, bw, 6*mm, fill=1, stroke=0)

        name = m.get('name','Unknown') or 'Unknown'
        species = m.get('species','') or ''
        cap_str = "★ CAPTAIN  " if is_cap else ""
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(TEXT_DARK if is_cap else TEXT)
        c.drawString(x + 2*mm, y - 4*mm, cap_str + name)

        c.setFont("Helvetica", 6)
        c.setFillColor(TEXT_DARK if is_cap else TEXT_DIM)
        c.drawRightString(x + bw - 2*mm, y - 4*mm, species)

        # Stats row
        sy = y - 13*mm
        stats = [
            ('REACT', m.get('reactions', 1)),
            ('SPEED', m.get('speed', '4"')),
            ('COMBAT', fmtsigned(m.get('combat', 0))),
            ('TOUGH', m.get('toughness', 3)),
            ('SAVVY', fmtsigned(m.get('savvy', 0))),
            ('LUCK', m.get('luck', 0)),
            ('XP', m.get('xp', 0)),
        ]
        stat_w = bw / len(stats)
        for j, (lbl, val) in enumerate(stats):
            sx = x + j * stat_w
            c.setFillColor(BG)
            c.setStrokeColor(BORDER)
            c.setLineWidth(0.3)
            c.rect(sx + 0.5, sy - 5*mm, stat_w - 1, 6*mm, fill=1, stroke=1)
            c.setFont("Helvetica", 5)
            c.setFillColor(TEXT_DIM)
            c.drawCentredString(sx + stat_w/2, sy - 1.5, lbl)
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(GOLD)
            c.drawCentredString(sx + stat_w/2, sy - 5*mm + 0.5, str(val))

        # Background / motivation / class row
        info_y = sy - 8*mm
        bg_str = m.get('background','') or ''
        mv_str = m.get('motivation','') or ''
        cl_str = m.get('charClass','') or ''
        armor  = m.get('armor','') or ''
        impl   = m.get('implants','') or ''
        c.setFont("Helvetica", 6)
        c.setFillColor(TEXT_DIM)
        c.drawString(x + 2*mm, info_y, "BG: ")
        c.setFillColor(TEXT)
        c.drawString(x + 8*mm, info_y, (bg_str or '—')[:22])
        c.setFillColor(TEXT_DIM)
        c.drawString(x + 2*mm, info_y - 4*mm, "MOT: ")
        c.setFillColor(TEXT)
        c.drawString(x + 9*mm, info_y - 4*mm, (mv_str or '—')[:22])
        c.setFillColor(TEXT_DIM)
        c.drawString(x + bw/2, info_y, "CLASS: ")
        c.setFillColor(TEXT)
        c.drawString(x + bw/2 + 11*mm, info_y, (cl_str or '—')[:18])
        if armor:
            c.setFillColor(TEXT_DIM)
            c.drawString(x + bw/2, info_y - 4*mm, "ARMOR: ")
            c.setFillColor(TEXT)
            c.drawString(x + bw/2 + 11*mm, info_y - 4*mm, armor)
        if impl:
            c.setFont("Helvetica", 5.5)
            c.setFillColor(TEXT_DIM)
            c.drawString(x + 2*mm, info_y - 8*mm, "IMPLANTS: ")
            c.setFillColor(TEXT)
            c.drawString(x + 16*mm, info_y - 8*mm, impl[:40])

        # Weapons
        weap_y = info_y - 13*mm
        c.setFillColor(BORDER)
        c.rect(x, weap_y + 3.5*mm, bw, 4*mm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 5.5)
        c.setFillColor(TEXT_DIM)
        heads = ['WEAPON', 'RANGE', 'SHOTS', 'DMG', 'TRAITS']
        col_ws = [bw*0.33, bw*0.12, bw*0.1, bw*0.08, bw*0.37]
        cx2 = x
        for head, cw in zip(heads, col_ws):
            c.drawString(cx2 + 1, weap_y + 5, head)
            cx2 += cw

        weapons = m.get('weapons', [])
        wy = weap_y - 1*mm
        for wi, wep in enumerate(weapons[:4]):
            wname = wep.get('customName') if wep.get('name') == 'Custom / Other' else wep.get('name','')
            if wi % 2 == 0:
                c.setFillColor(HexColor('#1a1e2e'))
                c.rect(x, wy - 3.5*mm, bw, 4*mm, fill=1, stroke=0)
            c.setFont("Helvetica", 6)
            c.setFillColor(TEXT)
            row_vals = [wname, str(wep.get('range','')), str(wep.get('shots','')), str(wep.get('damage','')), wep.get('traits','')]
            cx2 = x
            for rv, cw in zip(row_vals, col_ws):
                c.drawString(cx2 + 1, wy - 2, str(rv)[:int(cw/2)])
                cx2 += cw
            wy -= 4*mm

        # Gear
        gear_y = wy - 2*mm
        gear = [g for g in m.get('gear', []) if g]
        if gear:
            c.setFont("Helvetica", 5.5)
            c.setFillColor(TEXT_DIM)
            c.drawString(x + 2*mm, gear_y, "GEAR: ")
            c.setFillColor(TEXT)
            gear_str = ', '.join(gear)
            c.drawString(x + 10*mm, gear_y, gear_str[:65])
            gear_y -= 4*mm

        # Notes
        notes = (m.get('notes','') or '').strip()
        if notes:
            c.setFont("Helvetica-Oblique", 5.5)
            c.setFillColor(TEXT_DIM)
            c.drawString(x + 2*mm, gear_y, notes[:80])

    def draw_footer(c, w):
        c.setFont("Helvetica", 6)
        c.setFillColor(TEXT_DIM)
        c.drawCentredString(w/2, 10*mm, "Permission is granted to make copies of this form for personal use.  •  Five Parsecs from Home Third Edition  •  © Modiphius Entertainment")

    def fmtsigned(v):
        try:
            n = int(v)
            return f"+{n}" if n >= 0 else str(n)
        except:
            return str(v)

    draw_page_1()
    c.save()
    buf.seek(0)
    return buf.read()


class PDFHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  {self.address_string()} — {format % args}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path != '/pdf':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            crew = json.loads(body)
            pdf_bytes = make_crew_log_pdf(crew)
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="crew_log.pdf"')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(pdf_bytes)
            print(f"  ✓ PDF generated ({len(pdf_bytes):,} bytes) for crew: {crew.get('name','(unnamed)')}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))


if __name__ == '__main__':
    host, port = '127.0.0.1', 5678
    server = HTTPServer((host, port), PDFHandler)
    print("┌─────────────────────────────────────────────────────────┐")
    print("│   Five Parsecs from Home — Crew Log PDF Server          │")
    print(f"│   Listening on http://{host}:{port}                    │")
    print("│   Open index.html in your browser, then click Export PDF│")
    print("│   Press Ctrl+C to stop.                                 │")
    print("└─────────────────────────────────────────────────────────┘")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
