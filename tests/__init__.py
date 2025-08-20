# SPDX-FileCopyrightText: 2024-present Jeffrey Goldberg <jeffrey@goldmark.org>
#
# SPDX-License-Identifier: MIT

import os
import sys
from pathlib import Path

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, "src")
sys.path.append(SOURCE_PATH)

from toy_crypto import wycheproof  # noqa: E402


WP_ROOT = Path(os.path.dirname(__file__)) / "resources" / "wycheproof"
WP_DATA = wycheproof.Loader(WP_ROOT)
