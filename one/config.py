# SheerID 验证配置文件

# SheerID API 配置
PROGRAM_ID = '67c8c14f5f17a83b745e3f82'
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# 文件大小限制
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# 学校配置 - Multiple Universities (Anti-Pattern)
SCHOOLS = {
    '75': {
        'id': 75,
        'idExtended': '75',
        'name': 'Arizona State University',
        'city': 'Tempe',
        'state': 'AZ',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'ASU.EDU',
        'latitude': 33.42424,
        'longitude': -111.92805
    },
    '334': {
        'id': 334,
        'idExtended': '334',
        'name': 'University of Florida',
        'city': 'Gainesville',
        'state': 'FL',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'UFL.EDU',
        'latitude': 29.65163,
        'longitude': -82.32483
    },
    '339': {
        'id': 339,
        'idExtended': '339',
        'name': 'The Ohio State University',
        'city': 'Columbus',
        'state': 'OH',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'OSU.EDU',
        'latitude': 40.01419,
        'longitude': -83.03091
    },
    '2285': {
        'id': 2285,
        'idExtended': '2285',
        'name': 'New York University',
        'city': 'New York',
        'state': 'NY',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'NYU.EDU',
        'latitude': 40.72951,
        'longitude': -73.99646
    },
    '3499': {
        'id': 3499,
        'idExtended': '3499',
        'name': 'University of California-Los Angeles',
        'city': 'Los Angeles',
        'state': 'CA',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'UCLA.EDU',
        'latitude': 34.06892,
        'longitude': -118.44518
    },
    '3589': {
        'id': 3589,
        'idExtended': '3589',
        'name': 'University of Michigan-Ann Arbor',
        'city': 'Ann Arbor',
        'state': 'MI',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'UMICH.EDU',
        'latitude': 42.27804,
        'longitude': -83.73860
    },
    '3679': {
        'id': 3679,
        'idExtended': '3679',
        'name': 'University of Southern California',
        'city': 'Los Angeles',
        'state': 'CA',
        'country': 'US',
        'type': 'UNIVERSITY',
        'domain': 'USC.EDU',
        'latitude': 34.02235,
        'longitude': -118.28511
    }
}

# 默认学校
DEFAULT_SCHOOL_ID = '75'

# UTM 参数（营销追踪参数）
# 如果 URL 中没有这些参数，会自动添加
DEFAULT_UTM_PARAMS = {
    'utm_source': 'gemini',
    'utm_medium': 'paid_media',
    'utm_campaign': 'students_pmax_bts-slap'
}

