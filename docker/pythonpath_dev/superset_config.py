# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
import sys

from celery.schedules import crontab
from flask_caching.backends.filesystemcache import FileSystemCache

logger = logging.getLogger()

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_DB = os.getenv("DATABASE_DB")

EXAMPLES_USER = os.getenv("EXAMPLES_USER")
EXAMPLES_PASSWORD = os.getenv("EXAMPLES_PASSWORD")
EXAMPLES_HOST = os.getenv("EXAMPLES_HOST")
EXAMPLES_PORT = os.getenv("EXAMPLES_PORT")
EXAMPLES_DB = os.getenv("EXAMPLES_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

# Use environment variable if set, otherwise construct from components
# This MUST take precedence over any other configuration
SQLALCHEMY_EXAMPLES_URI = os.getenv(
    "SUPERSET__SQLALCHEMY_EXAMPLES_URI",
    (
        f"{DATABASE_DIALECT}://"
        f"{EXAMPLES_USER}:{EXAMPLES_PASSWORD}@"
        f"{EXAMPLES_HOST}:{EXAMPLES_PORT}/{EXAMPLES_DB}"
    ),
)


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "DATASET_FOLDERS": True,
    "ENABLE_EXTENSIONS": True,
    "SEMANTIC_LAYERS": True,
}
EXTENSIONS_PATH = "/app/docker/extensions"
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = f"http://superset_app{os.environ.get('SUPERSET_APP_ROOT', '/')}/"  # When using docker compose baseurl should be http://superset_nginx{ENV{BASEPATH}}/  # noqa: E501
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = (
    f"http://localhost:8888/{os.environ.get('SUPERSET_APP_ROOT', '/')}/"
)
SQLLAB_CTAS_NO_LIMIT = True

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)

if os.getenv("CYPRESS_CONFIG") == "true":
    # When running the service as a cypress backend, we need to import the config
    # located @ tests/integration_tests/superset_test_config.py
    base_dir = os.path.dirname(__file__)
    module_folder = os.path.abspath(
        os.path.join(base_dir, "../../tests/integration_tests/")
    )
    sys.path.insert(0, module_folder)
    from superset_test_config import *  # noqa

    sys.path.pop(0)

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa: F403

    logger.info(
        "Loaded your Docker configuration at [%s]", superset_config_docker.__file__
    )
except ImportError:
    logger.info("Using default Docker config...")

# Enable <style> tags for Handlebars chart CSS
HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
    "tagNames": ["style"]
}

# Brandfolder Beautiful Dashboards Color Schemes
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "bf_standard",
        "description": "Brandfolder Standard Theme",
        "label": "Brandfolder Standard",
        "colors": ["#E0EAFF", "#062A74", "#3D3D3D", "#2862DC", "#0F3B99", "#5886E9", "#FFC505", "#FF9705", "#A1D6FC", "#37CDC1", "#51CD37", "#FF5005"]
    },
    {
        "id": "bf_deep_space",
        "description": "Brandfolder Deep Space Theme",
        "label": "Brandfolder Deep Space",
        "colors": ["#9EF09E", "#5566FC", "#92B0FF", "#F5DC71", "#FF9C41", "#F55077"]
    },
    {
        "id": "bf_forest",
        "description": "Brandfolder Forest Theme",
        "label": "Brandfolder Forest",
        "colors": ["#FCFF66", "#ABD006", "#86A305", "#2BABA1", "#D6F5F2"]
    },
    {
        "id": "bf_starry_night",
        "description": "Brandfolder Starry Night Theme",
        "label": "Brandfolder Starry Night",
        "colors": ["#CDF80C", "#ABD006", "#86A305", "#5572AF", "#7D94C4", "#B8C6E5"]
    },
    {
        "id": "bf_retro",
        "description": "Brandfolder Retro Theme",
        "label": "Brandfolder Retro",
        "colors": ["#223459", "#6A5AAA", "#B45082", "#F9767F", "#FFB142", "#FFDE70"]
    },
    {
        "id": "bf_pastel",
        "description": "Brandfolder Pastel Theme",
        "label": "Brandfolder Pastel",
        "colors": ["#A0E0DA", "#16103C", "#A6BEF7", "#99E5FD", "#FADE80", "#FFB8BD"]
    },
    {
        "id": "bf_desert_sand",
        "description": "Brandfolder Desert Sand Theme",
        "label": "Brandfolder Desert Sand",
        "colors": ["#062A74", "#2862DC", "#78A0F7", "#B2792A", "#FFC505", "#E9E7E1"]
    },
    {
        "id": "bf_emerald",
        "description": "Brandfolder Emerald Theme",
        "label": "Brandfolder Emerald",
        "colors": ["#FF9705", "#C06944", "#324947", "#22867E", "#B2ECE7", "#EDE0CF"]
    },
    {
        "id": "bf_rainbow",
        "description": "Brandfolder Rainbow Theme",
        "label": "Brandfolder Rainbow",
        "colors": ["#FFC505", "#31D6AE", "#0B96F9", "#2862DC", "#062A74", "#BE55A7"]
    },
    {
        "id": "bf_sunny_surf",
        "description": "Brandfolder Sunny Surf Theme",
        "label": "Brandfolder Sunny Surf",
        "colors": ["#FF9705", "#062A74", "#034BE4", "#428BF9", "#B6CDFF", "#FAD1D4"]
    }
]

