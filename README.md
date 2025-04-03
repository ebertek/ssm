# Swedish Radiation Safety Authority (SSM) - Home Assistant Integration

This is a custom component for Home Assistant that integrates with the **Swedish Radiation Safety Authority (SSM)** to fetch radiation and UV data.

## Installation
### HACS (Recommended)
1. Go to **HACS**
2. Click on the three-dot menu (top right) and select **Custom repositories**
3. Add this Repository: `https://github.com/ebertek/ssm`
4. Select **Integration** as the Type
5. Search for `ssm`, select **Swedish Radiation Safety Authority**, click **Download**, and click **Download** again
6. Restart Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ebertek&repository=ssm&category=Integration)

### Manual Installation  
1. Copy the `custom_components/ssm` folder into your own `config/custom_components/`
2. Restart Home Assistant

## Configuration
1. Navigate to **Settings > Devices & services**
2. Click **Add integration** and search for `Swedish Radiation Safety Authority`
3. Select your **Station for Radiation Data**, enter your **Location Name for UV Index**, and enter your **Skin Type**
    1. To find your closest gamma radiation station, navigate to [SSM's radiation level site](https://karttjanst.ssm.se/gammastationer) or [REMon's radiological map](https://remap.jrc.ec.europa.eu/Advanced.aspx). You can find a mapping of location IDs, station names, and REMon IDs in the table below.
    2. To find your **Location Name for UV Index**, navigate to [SSM's UV-index site](https://www.stralsakerhetsmyndigheten.se/omraden/sol-och-solarier/uv-index/) and look under **Plats**.
    3. To find your **Skin Type**, please refer to **Solkänslighet** on [SSM's Min soltid site](https://www.minsoltid.se/).

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
