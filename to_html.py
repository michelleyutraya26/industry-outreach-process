import re
import html
from email_client import GmailClient

def _linkify_escaped(s: str) -> str:
    # Auto-link plain URLs (string is already escaped)
    return re.sub(r'(https?://[^\s<]+)', r'<a href="\1">\1</a>', s)

def _para_from_text(block: str) -> str:
    escaped = html.escape(block.strip())
    escaped = escaped.replace("\n", "<br/>")
    return f"<p>{_linkify_escaped(escaped)}</p>"

def _list_from_text(block: str) -> str:
    # Convert bullet lines (-, *, •) into <ul>
    items = []
    # If every non-empty line in the block starts with -, * or •, treats it as bullet list

    for line in block.strip().splitlines():
        m = re.match(r'^\s*[-*•]\s+(.*)$', line)
        if not m:
            # Mixed content → fall back to paragraph
            return _para_from_text(block)
        items.append(f"<li>{_linkify_escaped(html.escape(m.group(1)))}</li>")
    return f"<ul>{''.join(items)}</ul>"

def text_to_html(text: str) -> str:
    """Convert plain text to an HTML fragment (paragraphs, bullets, linkified URLs)."""
    if not text or not text.strip():
        return ""
    # Split on blank lines into blocks
    blocks = re.split(r'\n\s*\n+', text.strip())
    html_blocks = []
    for b in blocks:
        lines = [ln for ln in b.splitlines() if ln.strip()]
        if lines and all(re.match(r'^\s*[-*•]\s+', ln) for ln in lines):
            html_blocks.append(_list_from_text(b))
        else:
            html_blocks.append(_para_from_text(b))
    # <-- make sure return is OUTSIDE the loop
    return "\n".join(html_blocks)

def build_email_html(personalised_text:str, generic_text:str) -> str:
    personalized_html = text_to_html(personalized_text)
    generic_html = text_to_html(generic_text)
    return f"""\
    <div style="font-family:Arial,Segoe UI,sans-serif;font-size:14px;line-height:1.5;color:#111;">
      {personalized_html}
      <hr style="border:none;border-top:1px solid #eee;margin:16px 0;"/>
      {generic_html}
      <p style="margin-top:16px;">Best regards,<br/>DsCubed Recruitment Team</p>
    </div>"""


# Use triple quotes so you keep spaces/newlines
generic_text = """Dear Jane Street,

We have had the pleasure of collaborating with Jane Street in the past, and it was an incredibly rewarding experience for our member.

We truly appreciated the opportunity to work together and are excited about the potential to build on that partnership.
"""

personalized_text = "We at DSCubed would be thrilled to collaborate with Jane Street to provide our students with opportunities to engage in immersive internships and mentorship programs, aligning with your commitment to deep learning and innovative problem-solving. By partnering with us, Jane Street can inspire and empower the next generation of tech leaders through industry events and hands-on projects at the University of Melbourne."
body_html = build_email_html(generic_text, personalized_text)
print("\n--- HTML Email Preview ---\n", body_html, "\n")

