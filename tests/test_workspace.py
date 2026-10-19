
import unittest

from tools.workspace import list_workspace_files, read_workspace_file


class WorkspaceTests(unittest.TestCase):

    def test_lists_workspace_files(self):
        files = list_workspace_files()

        self.assertIn("README.md", files)
        self.assertIn("tools\\workspace.py", files)

    def test_excludes_internal_directories(self):
        files = list_workspace_files()

        for filename in files:
            parts = filename.replace("\\", "/").split("/")
            self.assertNotIn(".venv", parts)
            self.assertNotIn(".git", parts)
            self.assertNotIn("__pycache__", parts)

    def test_reads_workspace_file(self):
        content = read_workspace_file("tools/workspace.py")

        self.assertIn("WORKSPACE_ROOT", content)

    def test_blocks_path_traversal(self):
        with self.assertRaises(ValueError):
            read_workspace_file("..\\outside.txt")

    def test_rejects_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_workspace_file("missing_file.txt")


if __name__ == "__main__":
    unittest.main()
