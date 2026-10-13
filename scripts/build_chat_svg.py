"""Builds assets/chat.svg: an animated chat window for the profile README.

GitHub shows SVGs through <img>, which plays CSS animations but runs no
scripts, so every effect here is a CSS keyframe with a per-element delay.
Run:  python scripts/build_chat_svg.py
"""
from html import escape
from pathlib import Path

W = 820                      # canvas width
PAD = 28                     # inner padding of the chat area
BUBBLE_MAX = 470             # widest a bubble may be
LINE_H = 22                  # line height inside bubbles
CHAR_W = 7.9                 # rough width of one character at 15px
GAP = 12                     # space between bubbles
TYPING_S = 1.1               # how long "typing…" shows before a reply
READ_S = 0.9                 # pause after a message before the next one starts

# (who, text). "me" = Armielyn (left), "you" = visitor (right). "\n" forces a line break.
SCRIPT = [
    ("you", "hey! who are you?"),
    ("me", "Hi, I'm Armielyn. Developer Relations for AI & Web3."),
    ("me", "I help developers go from \"what is this?\"\nto \"I shipped it\"."),
    ("you", "nice. where do you work?"),
    ("me", "Right now: DevRel @ Rise In"),
    ("me", "Before that: Head of DevRel @ TARS AI\nand DevRel @ Virtuals Protocol / PathDAO"),
    ("me", "5,000+ builders onboarded across Southeast Asia\n100+ talks, workshops and demos"),
    ("you", "what are you building right now?"),
    ("me", "Doqtri: planned vs shipped, proven on Stellar\n→ doqtri.xyz"),
    ("you", "could you speak at our event?"),
    ("me", "Yes! DM me on X @aeriumcius. Let's build together."),
]


def wrap(text: str) -> list[str]:
    lines: list[str] = []
    max_chars = int((BUBBLE_MAX - 32) / CHAR_W)
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            candidate = f"{line} {word}".strip()
            if len(candidate) > max_chars and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


def build() -> str:
    parts: list[str] = []
    y = 104                  # first bubble's top (below the header)
    t = 0.6                  # seconds: when the next event starts
    for i, (who, text) in enumerate(SCRIPT):
        lines = wrap(text)
        width = min(BUBBLE_MAX, max(len(l) for l in lines) * CHAR_W + 32)
        height = len(lines) * LINE_H + 18
        x = PAD if who == "me" else W - PAD - width
        fill = "#1f2433" if who == "me" else "url(#you)"
        corner = (f"M{x+16},{y} H{x+width-16} Q{x+width},{y} {x+width},{y+16} V{y+height-16} "
                  f"Q{x+width},{y+height} {x+width-16},{y+height} H{x+16} Q{x},{y+height} {x},{y+height-16} "
                  f"V{y+16} Q{x},{y} {x+16},{y} Z")
        if who == "me":
            # typing indicator in the same slot, then the reply replaces it
            parts.append(
                f'<g class="typing" style="animation-delay:{t:.2f}s;animation-duration:{TYPING_S}s">'
                f'<rect x="{PAD}" y="{y}" width="64" height="36" rx="18" fill="#1f2433"/>'
                + "".join(f'<circle class="dot" style="animation-delay:{d*0.15:.2f}s" cx="{PAD+18+d*14}" cy="{y+18}" r="4"/>'
                          for d in range(3))
                + "</g>")
            t += TYPING_S
        parts.append(f'<g class="msg" style="animation-delay:{t:.2f}s">')
        parts.append(f'<path d="{corner}" fill="{fill}"/>')
        for n, line in enumerate(lines):
            color = "#e6e9f2" if who == "me" else "#ffffff"
            weight = ' font-weight="600"' if who == "me" and n == 0 and i == 1 else ""
            parts.append(f'<text x="{x+16}" y="{y+29+n*LINE_H}" fill="{color}"{weight}>{escape(line)}</text>')
        parts.append("</g>")
        y += height + GAP
        t += READ_S
    total_h = y + 70
    seen_at = t + 0.2

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total_h}" viewBox="0 0 {W} {total_h}" role="img" aria-label="Chat with Armielyn Obinguar, Developer Relations for AI and Web3">
<title>Chat with Armielyn Obinguar</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f0c29"/><stop offset="0.5" stop-color="#1b1840"/><stop offset="1" stop-color="#0d1117"/></linearGradient>
  <linearGradient id="you" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c5cff"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
  <linearGradient id="ava" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a78bfa"/><stop offset="1" stop-color="#302b63"/></linearGradient>
</defs>
<style>
  text {{ font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji", sans-serif; font-size: 15px; }}
  .msg {{ opacity: 0; transform-box: fill-box; transform-origin: center; animation: pop .45s cubic-bezier(.2,.9,.3,1.3) both; }}
  .typing {{ opacity: 0; animation-name: typing; animation-timing-function: linear; animation-fill-mode: both; }}
  .dot {{ fill: #8b93a7; animation: bounce 1s ease-in-out infinite; }}
  .seen {{ opacity: 0; animation: fade .4s ease-out both; animation-delay: {seen_at:.2f}s; }}
  .cursor {{ animation: blink 1s steps(1) infinite; }}
  @keyframes pop {{ 0% {{ opacity: 0; transform: translateY(14px) scale(.92); }} 100% {{ opacity: 1; transform: none; }} }}
  @keyframes typing {{ 0% {{ opacity: 0; }} 8% {{ opacity: 1; }} 88% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
  @keyframes bounce {{ 0%,60%,100% {{ transform: translateY(0); }} 30% {{ transform: translateY(-5px); }} }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .msg, .seen {{ animation: none; opacity: 1; }} .typing {{ display: none; }} }}
</style>
<rect width="{W}" height="{total_h}" rx="22" fill="url(#bg)"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{total_h-1}" rx="22" fill="none" stroke="#302b63"/>
<!-- header -->
<circle cx="{PAD+24}" cy="46" r="22" fill="url(#ava)"/>
<text x="{PAD+24}" y="52" text-anchor="middle" fill="#fff" font-weight="700" style="font-size:16px">AO</text>
<circle cx="{PAD+41}" cy="62" r="6" fill="#22c55e" stroke="#0f0c29" stroke-width="3"/>
<text x="{PAD+58}" y="42" fill="#fff" font-weight="700" style="font-size:17px">Armielyn Obinguar</text>
<text x="{PAD+58}" y="63" fill="#a78bfa" style="font-size:13px">● online · DevRel @ Rise In</text>
<text x="{W-PAD}" y="50" text-anchor="end" fill="#8b93a7" style="font-size:20px">⋯</text>
<line x1="{PAD}" y1="84" x2="{W-PAD}" y2="84" stroke="#2a2f45"/>
{chr(10).join(parts)}
<text class="seen" x="{W-PAD}" y="{y+2}" text-anchor="end" fill="#8b93a7" style="font-size:12px">Seen ✓✓</text>
<!-- composer -->
<rect x="{PAD}" y="{total_h-56}" width="{W-2*PAD-56}" height="40" rx="20" fill="#161a26" stroke="#2a2f45"/>
<text x="{PAD+18}" y="{total_h-31}" fill="#6b7389" style="font-size:14px">Say hi to Armielyn…<tspan class="cursor" fill="#a78bfa"> |</tspan></text>
<circle cx="{W-PAD-20}" cy="{total_h-36}" r="20" fill="url(#you)"/>
<path d="M{W-PAD-28},{total_h-44} L{W-PAD-10},{total_h-36} L{W-PAD-28},{total_h-28} L{W-PAD-24},{total_h-36} Z" fill="#fff"/>
</svg>
"""


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "chat.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print("wrote", out)
