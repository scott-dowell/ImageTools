from __future__ import annotations

import pytest

from scripts.prepare_test_images import prepare_copy


@pytest.fixture
def prepared_fixture_root():
    return prepare_copy()
