from __future__ import annotations

from os import getenv

AXES_ENABLED = getenv("AXES_ENABLED", default="true").lower() == "true"
AXES_FAILURE_LIMIT = int(getenv("AXES_FAILURE_LIMIT", default="5"))
AXES_CLIENT_IP_CALLABLE = None
# AXES_LOCKOUT_PARAMETERS = ["username_or_email"]
AXES_IPWARE_PROXY_ORDER = None
AXES_IPWARE_PROXY_COUNT = None
AXES_IPWARE_PROXY_TRUSTED_IPS = None
AXES_IPWARE_META_PRECEDENCE_ORDER = None
AXES_HANDLER = 'axes.handlers.dummy.AxesDummyHandler'