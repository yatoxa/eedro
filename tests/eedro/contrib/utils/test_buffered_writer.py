from eedro.contrib.utils.buffered_writer import (
    BufferedFileWriter,
    DelayedBufferedFileWriter,
)


def test_buffered_writer_flushes_data_on_context_exit(tmp_path):
    with BufferedFileWriter(
        base_dir=tmp_path, buffer_filename_prefix="records"
    ) as writer:
        writer.write("row-1")
        writer.write("row-2")

    files = list(tmp_path.glob("records*.data"))
    assert len(files) == 1
    assert files[0].read_text() == "row-1\nrow-2\n"


def test_buffered_writer_drains_on_size_limit(tmp_path):
    with BufferedFileWriter(base_dir=tmp_path, max_size=1) as writer:
        writer.write("first")
        writer.write("second")

    files = list(tmp_path.glob("*.data"))
    assert len(files) == 2
    assert sorted(file.read_text() for file in files) == ["first\n", "second\n"]


def test_delayed_buffered_writer_saves_data_to_file(tmp_path):
    with DelayedBufferedFileWriter(
        base_dir=tmp_path, buffer_filename_prefix="delayed"
    ) as writer:
        writer.writelines(["a", "b"])

    files = list(tmp_path.glob("delayed*.data"))
    assert len(files) == 1
    assert files[0].read_text() == "a\nb\n"
