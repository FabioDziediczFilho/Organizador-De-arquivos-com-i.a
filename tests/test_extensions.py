import pytest
from src.core.extensions import (
    get_file_category,
    get_supported_extensions,
    get_extensions_by_category,
    is_supported,
    get_all_categories
)

def test_get_file_category():
    assert get_file_category("image.jpg") == "imagem"
    assert get_file_category("IMAGE.JPEG") == "imagem"
    assert get_file_category("video.mp4") == "video"
    assert get_file_category("doc.pdf") == "desconhecido"
    assert get_file_category("no_extension") == "desconhecido"

def test_get_supported_extensions():
    extensions = get_supported_extensions()
    assert ".jpg" in extensions
    assert ".jpeg" in extensions
    assert ".png" in extensions
    assert ".mp4" in extensions
    assert len(extensions) == 4

def test_get_extensions_by_category():
    assert ".jpg" in get_extensions_by_category("imagem")
    assert ".mp4" in get_extensions_by_category("video")
    assert get_extensions_by_category("other") == []

def test_is_supported():
    assert is_supported("photo.png") is True
    assert is_supported("movie.mp4") is True
    assert is_supported("archive.zip") is False

def test_get_all_categories():
    categories = get_all_categories()
    assert "imagem" in categories
    assert "video" in categories
    assert len(categories) == 2
