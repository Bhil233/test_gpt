import argparse
import json
import mimetypes
from pathlib import Path

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload one image to script module and print the result."
    )
    parser.add_argument("image", help="Path to the image file")
    parser.add_argument(
        "--endpoint",
        default="http://127.0.0.1:8000/api/script/detect-fire",
        help="Detection API endpoint",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = Path(args.image).expanduser()

    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"

    with image_path.open("rb") as file_obj:
        files = {"file": (image_path.name, file_obj, mime_type)}
        response = httpx.post(args.endpoint, files=files, timeout=args.timeout)

    response.raise_for_status()

    try:
        payload = response.json()
    except ValueError:
        print(response.text)
        return

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
