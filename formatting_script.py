import re
import json
from pathlib import Path

def format_constitution(input_file, output_file, var_name="state"):
    """
    Convert an unformatted constitution text file into a structured JS file.
    
    Args:
        input_file (str | Path): Path to unformatted file
        output_file (str | Path): Path to save formatted JS file
        var_name (str): Variable name for output JS (default: "state")
    """
    # Load raw text
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Split into articles
    article_splits = re.split(r'\{article:"Article\s*', raw_text)
    articles = []

    for split in article_splits:
        if not split.strip():
            continue

        # Extract article number
        article_num_match = re.match(r'([^\s"]+)', split)
        article_num = article_num_match.group(1).replace('"', '') if article_num_match else ""

        # Extract article title
        title_match = re.search(r'title:"([^"]+)"', split)
        title = title_match.group(1) if title_match else ""

        # Parse sections
        sections = []
        section_splits = re.split(r'\nSection\s+(\d+[a-zA-Z\-]*)', split)

        if len(section_splits) > 1:
            # alternating [section_num, section_text, section_num, section_text,...]
            it = iter(section_splits[1:])
            for sec_num, sec_content in zip(it, it):
                sec_lines = sec_content.strip().splitlines()
                last_amended = None
                section_title = ""
                sec_text = ""

                # Look for "Last Amended ..." line
                if sec_lines and sec_lines[0].startswith("Last Amended"):
                    last_amended = sec_lines[0].replace("Last Amended", "").strip()
                    sec_lines = sec_lines[1:]

                # Section title
                if sec_lines:
                    section_title = sec_lines[0].strip()
                    sec_lines = sec_lines[1:]

                # Remaining lines = section text
                sec_text = " ".join(l.strip() for l in sec_lines if l.strip())

                section_obj = {
                    "section": f"Section {sec_num}",
                    "sectionTitle": section_title,
                    "secText": sec_text
                }
                if last_amended:
                    section_obj["lastAmended"] = last_amended

                sections.append(section_obj)

        # Build article object
        article_obj = {"article": f"Article {article_num}", "title": title, "text": sections}
        articles.append(article_obj)

    # Save to pretty-printed JS
    pretty_js = f"var {var_name} = " + json.dumps(articles, indent=2, ensure_ascii=False) + ";"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_js)

    print(f"Formatted constitution saved to {output_file}")


# Example usage:
# format_constitution("unformatted.js", "formatted_newyork.js", var_name="newyork")
