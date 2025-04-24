from __future__ import annotations

import logging
import random
import string
from datetime import timedelta
from typing import Any, ClassVar

from dj_rest_auth.registration.serializers import VerifyEmailSerializer

from dj_rest_auth.serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    UserDetailsSerializer,
)