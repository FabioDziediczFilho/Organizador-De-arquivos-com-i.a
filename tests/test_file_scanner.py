import pytest
import os
from src.core.file_scanner import (
    FileInfo,
    scan_directory,
    format_size,
    get_files_by_category,
    get_scan_summary
)

def test_file_info_class():
    file_info = FileInfo("/path/to/image.jpg", 1024, "imagem")
    assert file_info.path == "/path/to/image.jpg"
    assert file_info.size == 1024
    assert file_info.category == "imagem"
    assert file_info.name == "image.jpg"
    assert file_info.extension == ".jpg"

    info_dict = file_info.to_dict()
    assert info_dict["path"] == "/path/to/image.jpg"
    assert info_dict["size"] == 1024
    assert info_dict["category"] == "imagem"
    assert info_dict["name"] == "image.jpg"
    assert info_dict["extension"] == ".jpg"

def test_format_size():
    assert format_size(500) == "500.0 B"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(1024 * 1024 * 1024) == "1.0 GB"

def test_scan_directory(tmp_path):
    # Create temp directory structure
    d = tmp_path / "sub"
    d.mkdir()

    # Create files
    f1 = tmp_path / "image.jpg"
    f1.write_text("dummy content")

    f2 = d / "video.mp4"
    f2.write_text("dummy content")

    f3 = tmp_path / "unsupported.txt"
    f3.write_text("dummy content")

    # Non-recursive scan
    files_non_rec = scan_directory(str(tmp_path), recursive=False)
    assert len(files_non_rec) == 1
    assert files_non_rec[0].name == "image.jpg"

    # Recursive scan
    files_rec = scan_directory(str(tmp_path), recursive=True)
    assert len(files_rec) == 2
    names = [f.name for f in files_rec]
    assert "image.jpg" in names
    assert "video.mp4" in names

def test_get_files_by_category():
    files = [
        FileInfo("img1.jpg", 100, "imagem"),
        FileInfo("img2.png", 200, "imagem"),
        FileInfo("vid1.mp4", 500, "video")
    ]
    images = get_files_by_category(files, "imagem")
    assert len(images) == 2

    videos = get_files_by_category(files, "video")
    assert len(videos) == 1
    assert videos[0].name == "vid1.mp4"

def test_get_scan_summary():
    files = [
        FileInfo("img1.jpg", 1024, "imagem"),
        FileInfo("img2.png", 2048, "imagem"),
        FileInfo("vid1.mp4", 4096, "video")
    ]
    summary = get_scan_summary(files)
    assert summary["total_files"] == 3
    assert summary["total_size"] == 7168
    assert summary["total_size_formatted"] == "7.0 KB"
    assert summary["categories"]["imagem"] == 2
    assert summary["categories"]["video"] == 1
