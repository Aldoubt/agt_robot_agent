"""ROS2 package dependency analyzer for repo_audit.

Read-only helper that extracts package.xml dependencies.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


def analyze_ros_packages(workspace):
    results = []
    root = Path(workspace)

    for package_xml in root.rglob("package.xml"):
        try:
            tree = ET.parse(package_xml)
            package = tree.getroot()

            deps = []
            for tag in [
                "depend",
                "build_depend",
                "exec_depend",
                "test_depend",
                "buildtool_depend",
            ]:
                for item in package.findall(tag):
                    if item.text:
                        deps.append(item.text.strip())

            results.append(
                {
                    "path": str(package_xml.parent),
                    "name": package.findtext("name", default="unknown"),
                    "dependencies": sorted(set(deps)),
                }
            )
        except ET.ParseError:
            continue

    return results


def generate_dependency_markdown(packages, output):
    path = Path(output)
    with path.open("w", encoding="utf-8") as f:
        f.write("# ROS2 Dependency Report\n\n")
        for pkg in packages:
            f.write(f"## {pkg['name']}\n\n")
            f.write(f"Path: {pkg['path']}\n\n")
            f.write("Dependencies:\n")
            for dep in pkg["dependencies"]:
                f.write(f"- {dep}\n")
            f.write("\n")
