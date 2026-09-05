"""Geodetic transformation functions for Spatial Reference Resolver."""

from __future__ import annotations

import math
from typing import Tuple

# Krassovsky 1940 ellipsoid constants used in standard regional transforms
_A = 6378245.0
_EE = 0.00669342162296594323
_X_PI = math.pi * 3000.0 / 180.0


def _transform_lat(x: float, y: float) -> float:
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lon(x: float, y: float) -> float:
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lon: float, lat: float) -> Tuple[float, float]:
    """Converts WGS-84 coordinate to GCJ-02."""
    dlat = _transform_lat(lon - 105.0, lat - 35.0)
    dlon = _transform_lon(lon - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - _EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((_A * (1 - _EE)) / (magic * sqrtmagic) * math.pi)
    dlon = (dlon * 180.0) / (_A / sqrtmagic * math.cos(radlat) * math.pi)
    return lon + dlon, lat + dlat


def gcj02_to_wgs84(lon: float, lat: float) -> Tuple[float, float]:
    """Converts GCJ-02 coordinate to approximate WGS-84."""
    glon, glat = wgs84_to_gcj02(lon, lat)
    dlon = glon - lon
    dlat = glat - lat
    return lon - dlon, lat - dlat


def gcj02_to_bd09(lon: float, lat: float) -> Tuple[float, float]:
    """Converts GCJ-02 to BD-09."""
    z = math.sqrt(lon * lon + lat * lat) + 0.00002 * math.sin(lat * _X_PI)
    theta = math.atan2(lat, lon) + 0.000003 * math.cos(lon * _X_PI)
    bd_lon = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lon, bd_lat


def bd09_to_gcj02(lon: float, lat: float) -> Tuple[float, float]:
    """Converts BD-09 to GCJ-02."""
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * _X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * _X_PI)
    gcj_lon = z * math.cos(theta)
    gcj_lat = z * math.sin(theta)
    return gcj_lon, gcj_lat


def bd09_to_wgs84(lon: float, lat: float) -> Tuple[float, float]:
    """Converts BD-09 to WGS-84."""
    glon, glat = bd09_to_gcj02(lon, lat)
    return gcj02_to_wgs84(glon, glat)


def apply_missing_leading_digit(lon: float, lat: float) -> Tuple[float, float]:
    """Hypothesis K: Missing leading digit for China longitudes (e.g. 14.x -> 114.x, 8.x -> 108.x)."""
    if 0.0 < lon < 50.0:
        return lon + 100.0, lat
    return lon, lat


def apply_axis_swap(lon: float, lat: float) -> Tuple[float, float]:
    """Hypothesis R: Axis order swapped (lat, lon -> lon, lat)."""
    return lat, lon


def apply_empirical_shift(lon: float, lat: float, d_lon: float, d_lat: float) -> Tuple[float, float]:
    """Hypothesis E: Simple empirical planar translation."""
    return lon + d_lon, lat + d_lat
