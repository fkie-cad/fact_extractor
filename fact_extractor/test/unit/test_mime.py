import magic
from fact_extractor.helperFunctions.file_system import get_test_data_dir

def test_magic():
    # Ensures that all submodules of the extractor use the custom mime types
    import fact_extractor
    assert magic.from_file(f"{get_test_data_dir()}/ros_header", mime=True) == "firmware/ros", "firmware-magic-database is not loaded"

    assert magic.from_file(f"{get_test_data_dir()}/container/test.zip", mime=True) == "application/zip"
