from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.api.app.core.config import get_settings
from services.api.app.services.production import production_readiness

print(json.dumps(production_readiness(get_settings()), indent=2))
