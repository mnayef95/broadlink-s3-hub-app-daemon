- # Support broadlink s3 hub in AppDaemon

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs) [![](https://img.shields.io/github/v/release/mnayef95/broadlink-s3-hub-app-daemon.svg?include_prereleases&style=for-the-badge)](https://github.com/ericmatte/ad-media-lights-sync/releases)

<a href="https://www.buymeacoffee.com/mnayef95" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

## Installation

Use [HACS](https://hacs.xyz/) or download the `broadlink` directory from inside the `apps` directory here to your
local `apps` directory, then add the configuration to enable the `broadlink_s3_hub` module.

## App configuration

`config/appdaemon/apps/apps.yaml`

```yaml
broadlink_s3_hub:
  module: broadlink_s3_hub
  class: BroadlinkS3Hub
  hub_ip: "192.168.1.209"
  did: "00000000000000000000a043b0d059ac"
  scan_interval: 0.5
  friendly_names:
    - Balcony Light
  entity_ids:
    - light.balcony_app_demon_light
 ```

| key             | optional | type           | description                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------- | -------- |----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `module`        | False    | string         | The module name of the app.                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `class`         | False    | string         | The name of the Class.                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `friendly_name` | False    | list of string | The entity names that will be displayed in the frontend                                                                                                                                                                                                                                                                                                                                                                                                              |
| `hub_ip`        | False    | string         | The broadlink hub ip address                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `entity_id`     | False    | list of string | The entity ids that you will use to controll the entity in automations, the items in this array should same as the count of gangs in your switch if it's a switch                                                                                                                                                                                                                                                                                                    |
| `did`           | False    | string         | The device id that you want to control, check [this page](https://community.home-assistant.io/t/broadlink-s3-hub-support/319832/18?u=mnayef95) to know how to get it                                                                                                                                                                                                                                                                                                 |
| `scan_interval` | False    | int            | Platforms that require polling will be polled in an interval specified by the main component. For example a light will check every 30 seconds for a changed state. It is possible to overwrite this scan interval for any platform that is being polled by specifying a `scan_interval` configuration key. In the example below we set up the `your_lights` platform but tell Home Assistant to poll the devices every 10 seconds instead of the default 30 seconds. |

## Compatibility

This app should work with any sub device that you can add
to [s3 hub](https://www.ibroadlink.com/productinfo/778144.html).
That said, it has been tested and is working with the following devices:

- [BroadLink LC1-1 Gang Light Switch](https://www.amazon.co.uk/BroadLink-Neutral-Capacitor-Required-Compatible/dp/B096ZPL2TC?th=1)
