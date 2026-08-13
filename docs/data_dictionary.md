# Data Dictionary

## Restaurant Dataset

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| restaurant_id | String | Unique identifier | R001 |
| name | String | Restaurant name | Momo Hut |
| area | String | Main area/neighbourhood | Thamel |
| address | String | Publicly available address | Thamel Marg Kathmandu |
| latitude | Float | GPS latitude | 27.7128 |
| longitude | Float | GPS longitude | 85.3125 |
| cuisine | List | Cuisine tags (comma separated) | Nepali, Fast Food |
| price_level | String | low / medium / high | low |
| avg_price_per_person | Integer | Approx cost in NPR | 350 |
| rating | Float | Public rating (0-5) | 4.2 |
| review_count | Integer | Number of reviews | 1200 |
| veg_available | Boolean | Vegetarian options available | true |
| ambience_tags | List | Ambience descriptors | casual, lively |
| suitable_for | List | Purpose tags | friends, casual |
| opening_hours | String | Operating hours | 10:00 AM - 10:00 PM |
| source_url | String | Source URL | https://maps.google.com/... |
| description | String | Short description | Popular momo spot in Thamel... |
| data_confidence | String | high / medium / low | high |

### Areas Covered

Thamel, Patan, Boudha, Baneshwor, Jhamsikhel, Lazimpat, Durbarmarg, New Road, Baluwatar, Maharajgunj, Kupondole, Naxal

### Cuisine Categories

Nepali, Newari, Indian, Korean, Japanese, Chinese, Italian, Continental, Cafe, Bakery, Fast Food, Vegetarian, Multi-cuisine

### Price Levels

| Level | Typical Range (NPR) |
|-------|-------------------|
| low | Under 600 |
| medium | 600 - 1500 |
| high | Above 1500 |
