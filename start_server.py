"""Start script for the accessibility checker server."""

import uvicorn
from pathlib import Path
import sys

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

if __name__ == "__main__":
    print("=" * 60)
    print("PowerPoint & PDF Accessibility Checker")
    print("=" * 60)
    print()
    print("Starting server on http://localhost:8000")
    print("Press CTRL+C to stop")
    print()
    print("Open your browser and navigate to:")
    print("  → http://localhost:8000")
    print()
    print("=" * 60)

    uvicorn.run(
        "pptx_accessibility.api.app:app",
        host="localhost",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
