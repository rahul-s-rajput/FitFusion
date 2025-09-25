from pathlib import Path

for path in [Path('src/api/programs.py'), Path('src/utils/error_handler.py')]:
    print(f"=== {path} ===")
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if 'def _program_to_response' in line or 'def setup_sentry' in line or 'router' in line and 'APIRouter' in line:
            start = max(1, i-3)
            end = i+5
            for j in range(start, end+1):
                snippet_line = path.read_text().splitlines()[j-1]
                print(f"{j:04}: {snippet_line}")
            print()
            break
