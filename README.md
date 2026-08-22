# Fill Certificate Generator

A modular, extensible Python package and CLI tool to batch fill certificate image templates using participant CSV data.

## Features

- **Per-Event Directory Isolation**: Each event under `events/<event_name>/` contains its own `config.ini`, `templates/` folder, `data/` CSV files, and output `certs/`.
- **Flexible Field Configuration**: Fine-tune field positions (height, width, centering offsets), font sizes, custom font files, and text colors per field or globally in `config.ini`.
- **Multi-Event Batch Processing**: Process a single event or automatically discover and process all event directories at once.
- **Pillow 10+ Support**: Modern PIL text bounding box calculations for accurate centering and text alignment.
- **Automated Test Suite**: Unit tests included for configuration parsing, certificate rendering, and batch processing.

---

## Directory Structure

```text
fill_certificates/
├── fill_certificates/         # Modular Python package
│   ├── __init__.py
│   ├── config.py             # ConfigManager, EventConfig, FieldConfig
│   ├── generator.py          # CertificateGenerator (Pillow image drawing)
│   └── processor.py          # EventProcessor (CSV reader and batch runner)
├── events/                    # Event subdirectories
│   ├── d2d2026/               # Sample event folder
│   │   ├── config.ini         # Event configuration
│   │   ├── templates/         # Event templates directory
│   │   │   └── template.jpg
│   │   ├── data/              # Event CSV data directory
│   │   │   └── d2d2026.csv
│   │   └── certs/             # Generated certificates output
│   └── marathon_2026/
│       ├── config.ini
│       ├── templates/
│       │   └── template.jpg
│       ├── data/
│       │   └── marathon_2026.csv
│       └── certs/
├── main.py                    # CLI entry point
├── config.ini                 # Root configuration template
├── news-serif.ttf             # Font file
├── requirements.txt           # Python dependencies
└── tests/                     # Unit test suite
    ├── test_config.py
    ├── test_generator.py
    └── test_processor.py
```

---

## Configuration Guide (`config.ini`)

Each event directory under `events/<event_name>/` contains a `config.ini`:

```ini
[event]
template=templates/template.jpg
data_file=data/marathon_2026.csv
output_dir=certs
font_path=news-serif.ttf
text_color=20,40,80
name_field=name

[name]
height=300
font_size=56
width_offset_left=0
width_offset_right=0

[category]
height=420
font_size=36

[distance]
width=400
height=520
font_size=32

[time]
width=800
height=520
font_size=32
```

---

## Command Line Usage

### 1. List Available Events
```bash
python main.py --list-events
```

### 2. Process a Specific Event
```bash
python main.py --event d2d2026
```

Or pass a custom event directory path:
```bash
python main.py --event-dir events/d2d2026
```

### 3. Process All Events
```bash
python main.py --all
```

---

## Running Unit Tests

Run the test suite using Python's `unittest`:

```bash
python3 -m unittest discover -s tests
```
