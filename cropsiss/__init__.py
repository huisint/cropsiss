# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
"""Cross Platform Simultaneously Selling System"""
__version__ = "0.3.1"

from cropsiss import platforms


PLATFORMS: list[platforms.AbstractPlatform] = [
    platforms.Mercari(),
    platforms.YahooAuction()
]
