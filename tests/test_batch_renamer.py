import pytest
import os
from src.core.batch_renamer import BatchRenamer

def test_batch_renamer_pattern_extraction():
    renamer = BatchRenamer("/dummy")
    assert renamer._extract_pattern("foto123") == "foto"
    assert renamer._extract_pattern("ferias_2024_01") == "ferias_2024"
    assert renamer._extract_pattern("img_") == "img"
    assert renamer._extract_pattern("ab") == "ab"  # too short, falls back to original

def test_batch_renamer_suggest_folder_name():
    renamer = BatchRenamer("/dummy")
    assert renamer.suggest_folder_name("ferias_praia") == "Ferias praia"
    assert renamer.suggest_folder_name("viagem_março") == "Viagem março"

def test_batch_renamer_group_files_by_pattern():
    renamer = BatchRenamer("/dummy")
    files = [
        "/dummy/foto1.jpg",
        "/dummy/foto2.jpg",
        "/dummy/viagem1.jpg",
        "/dummy/other.jpg"
    ]
    groups = renamer.group_files_by_pattern(files)
    assert "foto" in groups
    assert "viagem" in groups
    assert len(groups["foto"]) == 2
    assert len(groups["viagem"]) == 1

def test_batch_renamer_rename_file(tmp_path):
    f = tmp_path / "old.jpg"
    f.write_text("data")

    renamer = BatchRenamer(str(tmp_path))
    new_path = renamer.rename_file(str(f), "new.jpg")

    assert os.path.exists(new_path)
    assert os.path.basename(new_path) == "new.jpg"
    assert not f.exists()

def test_batch_renamer_organize_by_pattern(tmp_path):
    f1 = tmp_path / "foto1.jpg"
    f1.write_text("data1")
    f2 = tmp_path / "foto2.jpg"
    f2.write_text("data2")
    f3 = tmp_path / "viagem1.jpg"
    f3.write_text("data3")

    renamer = BatchRenamer(str(tmp_path))
    files = [str(f1), str(f2), str(f3)]

    # Organize
    results = renamer.organize_by_pattern(files)

    assert len(results["moved"]) == 3
    assert len(results["errors"]) == 0

    # Check that folders were created and files were moved
    assert (tmp_path / "Foto").exists()
    assert (tmp_path / "Viagem").exists()
    assert (tmp_path / "Foto" / "foto1.jpg").exists()
    assert (tmp_path / "Foto" / "foto2.jpg").exists()
    assert (tmp_path / "Viagem" / "viagem1.jpg").exists()
