"""MCP CaptureViewport 결과(tool-results 파일)에서 base64 이미지를 PNG로 디코드.

CaptureViewport는 base64 PNG를 반환하는데 ~480만자라 에이전트 컨텍스트 토큰을 초과한다.
harness가 결과를 tool-results txt 파일로 저장하므로, 그 파일을 이 스크립트로 디코드한다
(Read로 열지 말 것 — 라인이 너무 길다).

사용:
    python decode_capture.py <tool-results.txt> <out.png>
그 뒤 Read <out.png> 로 확인.
"""
import json, base64, re, sys


def find_image_data(o):
    if isinstance(o, dict):
        img = o.get("image")
        if isinstance(img, dict) and isinstance(img.get("data"), str):
            return img["data"]
        for v in o.values():
            r = find_image_data(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_image_data(v)
            if r:
                return r
    return None


def main():
    if len(sys.argv) != 3:
        print("usage: python decode_capture.py <tool-results.txt> <out.png>")
        sys.exit(2)
    src, out = sys.argv[1], sys.argv[2]
    raw = open(src, encoding="utf-8", errors="replace").read()
    b64 = None
    try:
        b64 = find_image_data(json.loads(raw))
    except Exception:
        pass
    if not b64:  # fallback: regex for a long base64 "data" field
        m = re.search(r'"data"\s*:\s*"([A-Za-z0-9+/=]{1000,})"', raw)
        b64 = m.group(1) if m else None
    if not b64:
        print("NO BASE64 IMAGE FOUND in", src)
        sys.exit(1)
    with open(out, "wb") as f:
        f.write(base64.b64decode(b64))
    print("SAVED", out, "b64len", len(b64))


if __name__ == "__main__":
    main()
