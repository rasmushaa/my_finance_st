# docs/gen_ref_pages.py
from pathlib import Path
import mkdocs_gen_files

root = Path("src/backend")

nav = mkdocs_gen_files.Nav()

for path in sorted(root.rglob("*.py")):
    if path.name == "__init__.py":
        continue

    module_path = path.relative_to("src").with_suffix("")
    doc_path = Path("reference", *module_path.parts).with_suffix(".md")

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        identifier = ".".join(module_path.parts)
        print(f"::: {identifier}", file=fd)

    mkdocs_gen_files.set_edit_path(doc_path, path)
    nav[module_path.parts] = doc_path.as_posix()

# Write the navigation structure for mkdocs-literate-nav
with mkdocs_gen_files.open("SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
