"""Constants used by LeoNTP."""
import json
from pathlib import Path
from typing import Final

from homeassistant.const import Platform

SHOW_DEBUG_AS_WARNING = False

CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL = 10

PLATFORMS: Final = [Platform.SENSOR]

ATTRIBUTION: Final = "Data provided by LeoNTP"

PORT = 123

manifestfile = Path(__file__).parent / "manifest.json"
with open(manifestfile) as json_file:
    manifest_data = json.load(json_file)

DOMAIN = manifest_data.get("domain")
NAME = manifest_data.get("name")
VERSION = manifest_data.get("version")
ISSUEURL = manifest_data.get("issue_tracker")
STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
""".format(
    name = NAME, version = VERSION, issueurl = ISSUEURL
)

WEBSITE = "https://www.leobodnar.com/"
