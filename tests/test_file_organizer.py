import pytest
import os
from src.core.file_organizer import FileOrganizer
from src.core.file_scanner import FileInfo

def test_file_organizer(tmp_path):
    # Setup directories
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    # Create files to organize
    f1 = src_dir / "photo.jpg"
    f1.write_text("photo data")

    f2 = src_dir / "movie.mp4"
    f2.write_text("movie data")

    # Initialize FileOrganizer with base directory as the tmp_path
    organizer = FileOrganizer(str(tmp_path))

    files_to_organize = [
        FileInfo(str(f1), f1.stat().st_size, "imagem"),
        FileInfo(str(f2), f2.stat().st_size, "video")
    ]

    # Organize files
    results = organizer.organize_files(files_to_organize)

    assert results["total"] == 2
    assert len(results["moved"]) == 2
    assert len(results["errors"]) == 0

    # Check that directories were created and files were moved
    dest_img_dir = tmp_path / "imagem"
    dest_vid_dir = tmp_path / "video"

    assert dest_img_dir.exists()
    assert dest_vid_dir.exists()

    assert (dest_img_dir / "photo.jpg").exists()
    assert (dest_vid_dir / "movie.mp4").exists()

    # Check duplicate handling
    f3 = src_dir / "photo2.jpg"
    f3.write_text("another photo")

    # If we move a file with same name to 'imagem'
    f_dup = src_dir / "photo.jpg"
    f_dup.write_text("different data")

    file_info_dup = FileInfo(str(f_dup), f_dup.stat().st_size, "imagem")
    dest_path = organizer.move_file_to_category(file_info_dup)

    assert os.path.exists(dest_path)
    assert os.path.basename(dest_path) == "photo_1.jpg"
