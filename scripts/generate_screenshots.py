#!/usr/bin/env python3
"""Generate README demo screenshots from a live API response."""

import json
import textwrap
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "screenshots"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/consola.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(text: str, width: int = 88) -> str:
    lines: list[str] = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            lines.append("")
            continue
        lines.extend(textwrap.wrap(paragraph, width=width) or [""])
    return "\n".join(lines)


def draw_card(title: str, body: str, filename: str, *, width: int = 1280, padding: int = 36) -> None:
    font_title = load_font(30)
    font_body = load_font(22)
    wrapped = wrap_text(body)
    line_height = 30
    body_lines = wrapped.split("\n")
    height = padding * 2 + 50 + len(body_lines) * line_height + 20

    img = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 56), fill="#1f2937")
    draw.text((padding, 12), title, fill="#f9fafb", font=font_title)

    y = padding + 40
    for line in body_lines:
        draw.text((padding, y), line, fill="#e5e7eb", font=font_body)
        y += line_height

    img.save(OUT_DIR / filename)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    response = httpx.post(
        "http://localhost:8000/api/v1/query",
        json={"question": "销量最高的3个产品是什么？"},
        timeout=120.0,
    )
    response.raise_for_status()
    data = response.json()

    (OUT_DIR / "sample-response.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    swagger_body = "\n".join(
        [
            "POST /api/v1/query",
            "Status: 200 OK",
            "",
            "Request:",
            json.dumps({"question": data["question"]}, ensure_ascii=False, indent=2),
            "",
            "Response:",
            json.dumps(
                {
                    "answer": data["answer"],
                    "sql": data["sql"],
                    "rows": data["rows"][:3],
                    "latency_ms": data["latency_ms"],
                },
                ensure_ascii=False,
                indent=2,
            ),
        ]
    )
    draw_card("Swagger Demo - SQL Agent", swagger_body, "swagger-demo.png")

    steps_lines = []
    for item in data.get("steps", []):
        if item.get("type") == "tool_call":
            steps_lines.append(
                f"Step {item['step']} | tool={item['tool']} | input={json.dumps(item.get('input', {}), ensure_ascii=False)}"
            )
            obs = item.get("observation", "")
            steps_lines.append(f"  observation: {obs[:180]}{'...' if len(obs) > 180 else ''}")
        else:
            steps_lines.append(
                f"Step {item['step']} | {item.get('type')} | {item.get('content', '')[:200]}"
            )

    trace_body = "\n".join(steps_lines) or "No steps returned."
    draw_card("ReAct Steps Trace", trace_body, "steps-trace.png", width=1280)

    print(f"Generated screenshots in {OUT_DIR}")


if __name__ == "__main__":
    main()
