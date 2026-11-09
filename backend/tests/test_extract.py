from app.integrations.extract import extract_text, ocr_available


def test_extract_plain_text():
    assert extract_text("note.txt", "text/plain", b"hello world") == "hello world"


def test_extract_markdown_by_extension():
    assert extract_text("a.md", None, b"# Title") == "# Title"


def test_image_garbage_returns_empty():
    # Invalid image bytes yield no text whether or not Tesseract is installed.
    assert extract_text("scan.png", "image/png", b"not a real image") == ""


def test_unknown_type_returns_empty():
    assert extract_text("x.bin", "application/octet-stream", b"\x00\x01") == ""


def test_ocr_available_is_bool():
    assert isinstance(ocr_available(), bool)
