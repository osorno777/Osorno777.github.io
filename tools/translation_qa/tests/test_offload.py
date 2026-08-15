import json
from pathlib import Path

from translation_qa.offload import offload_work_to_drive, qa_layout


def test_offload_moves_reports_and_patches_output_dir(tmp_path: Path):
    repo = tmp_path / "repo"
    drive = tmp_path / "E"
    reports = repo / "reports"
    reports.mkdir(parents=True)
    (reports / "bearing-the-cross-3__btc-3_af__af.html").write_text("<html>ok</html>", encoding="utf-8")
    (reports / "bearing-the-cross-3__btc-3_af__af.json").write_text("{}", encoding="utf-8")
    cache = repo / "translation_qa" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "cli.cpython-314.pyc").write_bytes(b"pyc")
    (repo / "paths.example.json").write_text('{"output_dir": "./reports"}\n', encoding="utf-8")

    result = offload_work_to_drive(drive, repo, require_root_exists=False)

    layout = qa_layout(drive)
    assert Path(result["reports"]) == layout["reports"]
    assert (layout["reports"] / "bearing-the-cross-3__btc-3_af__af.html").is_file()
    assert not (reports / "bearing-the-cross-3__btc-3_af__af.html").exists()
    assert not (cache / "cli.cpython-314.pyc").exists()
    cfg = json.loads((repo / "paths.json").read_text(encoding="utf-8"))
    assert Path(cfg["output_dir"]) == layout["reports"]
    assert result["moved"] >= 2


def test_offload_keeps_existing_e_drive_html(tmp_path: Path):
    repo = tmp_path / "repo"
    drive = tmp_path / "E"
    (repo / "reports").mkdir(parents=True)
    (repo / "reports" / "same.html").write_text("from-c", encoding="utf-8")
    dest = qa_layout(drive)["reports"]
    dest.mkdir(parents=True)
    (dest / "same.html").write_text("from-e", encoding="utf-8")
    (repo / "paths.example.json").write_text("{}", encoding="utf-8")

    offload_work_to_drive(drive, repo, require_root_exists=False)

    assert (dest / "same.html").read_text(encoding="utf-8") == "from-e"
    assert not (repo / "reports" / "same.html").exists()


def test_use_drive_cli_writes_e_layout(tmp_path: Path):
    from translation_qa.cli import main

    repo = tmp_path / "repo"
    drive = tmp_path / "E"
    (repo / "reports").mkdir(parents=True)
    (repo / "reports" / "btc-3__btc-3_af__af.html").write_text("<html>ok</html>", encoding="utf-8")
    (repo / "paths.example.json").write_text('{"output_dir": "./reports"}\n', encoding="utf-8")

    assert main(["use-drive", "--root", str(drive), "--repo", str(repo)]) == 0
    layout = qa_layout(drive)
    assert (layout["reports"] / "btc-3__btc-3_af__af.html").is_file()
    cfg = json.loads((repo / "paths.json").read_text(encoding="utf-8"))
    assert Path(cfg["output_dir"]) == layout["reports"]
