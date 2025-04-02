# Swedish Radiation Safety Authority (SSM) - Home Assistant Integration

This is a custom component for Home Assistant that integrates with the **Swedish Radiation Safety Authority (SSM)** to fetch radiation and UV data.

## Installation
### HACS (Recommended)
1. Go to **HACS > Integrations**
2. Click on the three-dot menu (top right) and select **Custom Repositories**
3. Add this repository: `https://github.com/ebertek/ssm`
4. Select **Integration** as the category
5. Install and restart Home Assistant

### Manual Installation  
1. Copy the `ssm` folder into `config/custom_components/`
2. Restart Home Assistant

## Configuration
1. Navigate to **Settings > Devices & services**
2. Click **Add integration** and search for `Swedish Radiation Safety Authority`
3. Enter your **Location ID** and **Location Name**
    1. To find your closest gamma radiation station, navigate to [SSM's radiation level site](https://karttjanst.ssm.se/gammastationer) or [REMon's radiological map](https://remap.jrc.ec.europa.eu/Advanced.aspx) and use the table below to find your **Location ID for Radiation Data**
    2. To find your **Location Name for UV Index**, navigate to [SSM's UV-index site](https://www.stralsakerhetsmyndigheten.se/omraden/sol-och-solarier/uv-index/) and look under *Plats*

| Location ID |         Station         | REMon ID |
| ----------- | ----------------------- | -------- |
|          20 | Bjuruklubb (Skellefteå) |  SE0058  |
|           5 | Brämön                  |  SE0047  |
|           7 | Fårösund                |  SE0053  |
|          18 | Gielas (Kittelfjäll)    |  SE0060  |
|           8 | Gävle                   |  SE0048  |
|          17 | Göteborg                |  SE0062  |
|          16 | Hallands Väderö         |  SE0063  |
|          21 | Hällum                  |  SE0067  |
|           6 | Järnäsklubb             |  SE0046  |
|          11 | Karesuando              |  SE0051  |
|        1278 | Kilsbergen              |  SE0066  |
|           4 | Krångede                |    --    |
|          22 | Malmö                   |  SE0064  |
|          19 | Malå                    |  SE0059  |
|           2 | Mora                    |  SE0043  |
|        1276 | Norrköping              |  SE0040  |
|          12 | Pajala                  |  SE0050  |
|           9 | Ritsem                  |  SE0052  |
|           1 | Sala                    |  SE0042  |
|          25 | Skarpö                  |  SE0068  |
|          14 | Skillinge               |  SE0057  |
|          10 | Storön                  |    --    |
|          15 | Sunne                   |    --    |
|           3 | Tännäs                  |  SE0044  |
|          24 | Visingsö                |  SE0061  |
|        1277 | Växjö                   |  SE0054  |
|          23 | Ölands Norra Udde       |  SE0055  |
|          13 | Ölands Södra Udde       |  SE0056  |

## License
This project is licensed under the [Apache License 2.0](LICENSE).