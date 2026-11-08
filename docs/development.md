# Development

This page describes how the Operator PC repository is organized and built: the Docker
image, the ROS 2 package, the VS Code tasks, the documentation and CI. The Robot PC has
its own
[development page](https://systemfromscratch.github.io/sfs-smartmanipulator-x-robot/development/).

## Repository layout

```text
.
├── docker/
│   ├── Dockerfile                    Operator PC image (ros:jazzy-ros-base + MoveIt 2 + RViz2 + workspace)
│   ├── docker-compose.yml            operator_pc and shell services on smx_net
│   ├── entrypoint.sh                 sources ROS 2 and the built workspace
│   └── env.example                   template for docker/.env
├── ros2_ws/src/
│   └── smartmanipulator_x_moveit_config/   SRDF, kinematics, limits, controllers, launch, RViz2
├── tools/docs/                       PDF manual builder, figures, MkDocs hook
├── docs/, overrides/, mkdocs.yml     this documentation
├── requirements-docs.txt             documentation tools (.venv)
└── .vscode/tasks.json                Operator PC and documentation tasks
```

Generated directories (`ros2_ws/build/`, `ros2_ws/install/`, `ros2_ws/log/`, `site/`,
`build/`, `docs/downloads/`, `.venv/`) are ignored by Git, and the documentation is kept
out of the Docker build context by `.dockerignore`.

## Working on the MoveIt configuration

The workspace is built into the image, not bind-mounted. After a change under
`ros2_ws/src/`:

```bash
docker compose -f docker/docker-compose.yml up --build operator_pc
```

Rules that keep the two computers consistent:

- Do not add a URDF/Xacro here. Change the robot description in the Robot PC repository
  and rebuild both images.
- Joint names, planning groups, controller names and the joints of each controller must
  match `smartmanipulator_x_description` and the Robot PC's `controllers.yaml`.
- Keep Operator-only dependencies (MoveIt, RViz2, Gazebo, GUI libraries) in this image;
  never add them to the Robot PC image.
- The Operator PC gets no USB device and no `ros2_control` hardware interface.

For a quick test of a configuration file without a rebuild, mount it over the installed
copy, for example:

```bash
docker compose -f docker/docker-compose.yml run --rm \
    -v "$PWD/ros2_ws/src/smartmanipulator_x_moveit_config/config:/ws/install/smartmanipulator_x_moveit_config/share/smartmanipulator_x_moveit_config/config" \
    operator_pc
```

Stop `operator_pc` first (fixed address); rebuild before you commit.

## VS Code tasks

`.vscode/tasks.json` runs Docker Compose from the repository root. **Ctrl+Shift+B** opens
a picker with every task of the build group; none is the default, so the picker always
appears.

| Task | Group | Command |
| --- | --- | --- |
| Operator PC: Start (move_group + RViz2) | build | `docker compose -f docker/docker-compose.yml up --build operator_pc` |
| Operator PC: Stop | build | `docker compose -f docker/docker-compose.yml down` |
| Operator PC: Rebuild and restart | build | Stop, then `up --build --force-recreate operator_pc` |
| Operator PC: Build image | build | `build operator_pc` |
| Operator PC: Rebuild image (no cache) | build | `build --no-cache --pull operator_pc` |
| Docs: Build PDF manual | build | `python tools/docs/build_manual.py` in `.venv` |
| Operator PC: Shell | – | `run --rm shell` |
| Docs: Live preview | – | `mkdocs serve` in `.venv` |

## Documentation

The documentation is the Markdown in `docs/`. MkDocs Material turns it into the website,
and `tools/docs/build_manual.py` turns the same pages into the printable A4 user manual
(cover, imprint, contents with page numbers, numbered chapters, running headers, PDF
bookmarks), rendered with WeasyPrint. Both follow the SystemFromScratch® documentation
style of the Robot PC documentation; the landing page is configured in
`mkdocs.yml → extra.landing` and the manual in `mkdocs.yml → extra.manual`.

Set up the tools once in the repository `.venv`. WeasyPrint needs the Pango library: on
Windows from MSYS2 (`pacman -S mingw-w64-x86_64-pango`; the builder finds
`C:\msys64\mingw64\bin` by itself), on Ubuntu `apt install libpango-1.0-0 libpangoft2-1.0-0`.

```powershell
# Windows (PowerShell, repository root)
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
```

```bash
# Linux (repository root)
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-docs.txt
```

| Command | Result |
| --- | --- |
| `python -m mkdocs serve` | Live preview at <http://127.0.0.1:8000> |
| `python -m mkdocs build` | Static website in `site/` (strict: a broken link fails the build) |
| `python tools/docs/build_manual.py` | `build/manual/SmartManipulator-X_Operator_PC_User_Manual_v<version>.pdf`; the version is the latest `vX.Y.Z` tag |
| `python tools/docs/build_manual.py --output docs/downloads/SmartManipulator-X_Operator_PC_User_Manual.pdf` | The file the website links to (CI does this before deploying) |
| `python tools/docs/diagrams.py` | Regenerates the hero `docs/assets/images/hero-3d.svg` and the diagrams `system-overview.svg`, `ros-graph.svg`, `control-paths.svg`, `smx-net.svg`, `image-build.svg` |
| `python tools/docs/diagrams.py --no-hero` | Only the diagrams (no Robot PC checkout needed) |

The hero draws the real arm: `tools/docs/hero_robot.py` reads the URDF/Xacro and the
visual meshes of `smartmanipulator_x_description` from the Robot PC repository
(`SMX_ROBOT_PC_REPO`, default `../SmartManipulator-X-Robot-PC`) and places them by forward
kinematics; the glowing tool path above the arm is the fingertip position computed the
same way. Run it again after the description changes.

Writing rules that keep the website and the PDF correct:

- Start every page with exactly one `# Title`; chapter and section numbers are added in
  the PDF, so do not number headings by hand.
- Add a new page to `nav` in `mkdocs.yml`, otherwise it is missing from the site and the
  PDF.
- An image on a line of its own, `![Caption](assets/images/file.svg)`, becomes a figure
  with its alt text as the caption (`tools/docs/hooks.py`).
- Link to other pages with relative `.md` paths; strict mode checks them, and the PDF
  turns them into page references.
- Diagrams are SVG files generated by `tools/docs/diagrams.py`; the PDF renderer runs no
  JavaScript.
- Every value in the documentation (addresses, limits, parameters) comes from the files
  of this repository or the Robot PC repository; change the page together with the file.

## CI

| Workflow | Trigger | Does |
| --- | --- | --- |
| `documentation.yml` | Push to `main`; manual | Builds the PDF manual into `docs/downloads/`, then `mkdocs gh-deploy` publishes the website with the PDF to GitHub Pages (branch `gh-pages`) |

Enable GitHub Pages for the `gh-pages` branch in the repository settings once; the site
is then at <https://systemfromscratch.github.io/sfs-smartmanipulator-x-operator/>.
