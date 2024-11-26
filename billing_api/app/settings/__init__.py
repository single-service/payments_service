import os
from app.settings.common import CommonConfig

settings_classes = {
    'common': CommonConfig,
}

settings: CommonConfig = settings_classes[os.environ.get('OSM_SETTINGS', 'common')]
