<img src="https://github.com/CumpsD/home-assistant-leo-ntp/raw/main/images/brand/icon@2x.png"
     alt="LeoNTP"
     align="right"
     style="width: 124px;margin-right: 10px;" />

# LeoNTP for Home Assistant

A Home Assistant integration to monitor LeoNTP

### Features

- All possible LeoNTP 1200 sensors.

---

[![maintainer](https://img.shields.io/badge/maintainer-David%20Cumps-green?style=for-the-badge&logo=github)](https://github.com/CumpsD) [![MIT License](https://img.shields.io/github/license/CumpsD/home-assistant-leo-ntp?style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/blob/master/LICENSE) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

<!-- [![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)

[![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CumpsD&repository=home-assistant-leo-ntp&category=integration) -->

[![manifest version](https://img.shields.io/github/manifest-json/v/CumpsD/home-assistant-leo-ntp/master?filename=custom_components%2Fleo_ntp%2Fmanifest.json&style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp)
[![github release](https://img.shields.io/github/v/release/CumpsD/home-assistant-leo-ntp?logo=github&style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/releases)
[![github release date](https://img.shields.io/github/release-date/CumpsD/home-assistant-leo-ntp?style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/releases)

[![github contributors](https://img.shields.io/github/contributors/CumpsD/home-assistant-leo-ntp?style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/graphs/contributors)
[![github commit activity](https://img.shields.io/github/commit-activity/y/CumpsD/home-assistant-leo-ntp?logo=github&style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/commits/main)
[![github last-commit](https://img.shields.io/github/last-commit/CumpsD/home-assistant-leo-ntp?style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/commits)

[![Code Linting](https://img.shields.io/github/actions/workflow/status/CumpsD/home-assistant-leo-ntp/lint.yml?label=lint&style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/actions/workflows/lint.yml)
[![Hacs and Hassfest validation](https://img.shields.io/github/actions/workflow/status/CumpsD/home-assistant-leo-ntp/validate.yml?label=validate&style=for-the-badge)](https://github.com/CumpsD/home-assistant-leo-ntp/actions/workflows/validate.yml)

## Installation

### Manual

1. Copy the `custom_components/leo_ntp` directory of this repository as `config/custom_components/leo_ntp` in your Home Assistant installation.
2. Restart Home Assistant.
3. Add the '`leo_ntp`' integration via HA Settings > '`Devices and Services`' > '`Integrations`'.
4. Provide the IP address of your LeoNTP.

This integration will set up the following platforms.

| Platform  | Description                                     |
| --------- | ----------------------------------------------- |
| `leo_ntp` | Home Assistant component for LeoNTP             |

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Troubleshooting

1. You can enable logging for this integration specifically and share your logs, so I can have a deep dive investigation. To enable logging, update your `configuration.yaml` like this, so we can get more information in the `Configuration` -> `Logs` page.

```
logger:
  default: warning
  logs:
    custom_components.leo_ntp: debug
```

## Screenshots

![LeoNTP Lovelace](https://github.com/CumpsD/home-assistant-leo-ntp/raw/main/images/leo_ntp.png "LeoNTP Lovelace")
