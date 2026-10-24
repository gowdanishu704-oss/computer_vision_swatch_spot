"""
EXIF Metadata and Geotag Extractor for Citizen Uploads.
Extracts GPS Latitude/Longitude, Timestamp, Camera info, and provides EXIF injection for testing.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags
import piexif
import io


def _convert_to_degrees(value) -> float:
    """Helper to convert the GPS coordinates stored in EXIF to decimal degrees."""
    try:
        # Some libraries return IFDRational or tuples (num, denom)
        def _to_float(v):
            if isinstance(v, (int, float)):
                return float(v)
            if hasattr(v, 'numerator') and hasattr(v, 'denominator'):
                return v.numerator / (v.denominator or 1)
            if isinstance(v, (tuple, list)) and len(v) == 2:
                return v[0] / (v[1] or 1)
            return float(v)

        d = _to_float(value[0])
        m = _to_float(value[1])
        s = _to_float(value[2])

        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return 0.0


def extract_geotags(image_input) -> Dict[str, Any]:
    """
    Extracts geotagging and EXIF metadata from a PIL Image or file-like object.
    
    Returns:
        dict with keys:
            - has_gps: bool
            - latitude: Optional[float]
            - longitude: Optional[float]
            - timestamp: Optional[str]
            - device: Optional[str]
            - raw_exif_found: bool
    """
    result = {
        "has_gps": False,
        "latitude": None,
        "longitude": None,
        "timestamp": None,
        "device": "Unknown Device",
        "raw_exif_found": False
    }

    try:
        if hasattr(image_input, "read") and not hasattr(image_input, "getexif"):
            try:
                image_input.seek(0)
            except Exception:
                pass
            img = Image.open(image_input)
        elif isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
        else:
            img = image_input

        # 1. First attempt: Pillow getexif()
        exif_raw = None
        if hasattr(img, "getexif"):
            try:
                exif_raw = img.getexif()
            except Exception:
                exif_raw = None

        if exif_raw:
            result["raw_exif_found"] = True

            # Extract standard tags (Make, Model, DateTime)
            make = exif_raw.get(ExifTags.Base.Make.value, "")
            model = exif_raw.get(ExifTags.Base.Model.value, "")
            if make or model:
                result["device"] = f"{make} {model}".strip()

            dt = exif_raw.get(ExifTags.Base.DateTime.value, "")
            if dt:
                result["timestamp"] = str(dt)

            # GPS Info is in IFD sub-directory
            gps_ifd = None
            try:
                gps_ifd = exif_raw.get_ifd(ExifTags.IFD.GPSInfo.value)
            except Exception:
                pass

            if not gps_ifd:
                # Check Base tag directly
                for tag_id, val in exif_raw.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag_name == "GPSInfo" and isinstance(val, dict):
                        gps_ifd = val
                        break

            if gps_ifd:
                lat_val = gps_ifd.get(2) or gps_ifd.get(ExifTags.GPS.GPSLatitude.value)
                lat_ref = gps_ifd.get(1) or gps_ifd.get(ExifTags.GPS.GPSLatitudeRef.value, "N")
                lon_val = gps_ifd.get(4) or gps_ifd.get(ExifTags.GPS.GPSLongitude.value)
                lon_ref = gps_ifd.get(3) or gps_ifd.get(ExifTags.GPS.GPSLongitudeRef.value, "E")

                if lat_val and lon_val:
                    lat = _convert_to_degrees(lat_val)
                    lon = _convert_to_degrees(lon_val)

                    if isinstance(lat_ref, bytes):
                        lat_ref = lat_ref.decode(errors="ignore")
                    if isinstance(lon_ref, bytes):
                        lon_ref = lon_ref.decode(errors="ignore")

                    if str(lat_ref).strip().upper() == "S":
                        lat = -lat
                    if str(lon_ref).strip().upper() == "W":
                        lon = -lon

                    if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and (lat != 0.0 or lon != 0.0):
                        result["has_gps"] = True
                        result["latitude"] = round(lat, 6)
                        result["longitude"] = round(lon, 6)

        # 2. Secondary fallback attempt: piexif on raw exif bytes
        if not result["has_gps"] and hasattr(img, "info") and "exif" in img.info:
            try:
                raw_exif = img.info["exif"]
                piex_dict = piexif.load(raw_exif)
                result["raw_exif_found"] = True

                # Check device from 0th IFD
                zeroth = piex_dict.get("0th", {})
                make_b = zeroth.get(piexif.ImageIFD.Make, b"")
                model_b = zeroth.get(piexif.ImageIFD.Model, b"")
                if make_b or model_b:
                    dev_str = f"{make_b.decode(errors='ignore')} {model_b.decode(errors='ignore')}".strip()
                    if dev_str:
                        result["device"] = dev_str

                gps_dict = piex_dict.get("GPS", {})
                if gps_dict:
                    lat_val = gps_dict.get(piexif.GPSIFD.GPSLatitude)
                    lat_ref = gps_dict.get(piexif.GPSIFD.GPSLatitudeRef, b"N")
                    lon_val = gps_dict.get(piexif.GPSIFD.GPSLongitude)
                    lon_ref = gps_dict.get(piexif.GPSIFD.GPSLongitudeRef, b"E")

                    if lat_val and lon_val:
                        lat = _convert_to_degrees(lat_val)
                        lon = _convert_to_degrees(lon_val)

                        if isinstance(lat_ref, bytes):
                            lat_ref = lat_ref.decode(errors="ignore")
                        if isinstance(lon_ref, bytes):
                            lon_ref = lon_ref.decode(errors="ignore")

                        if str(lat_ref).strip().upper() == "S":
                            lat = -lat
                        if str(lon_ref).strip().upper() == "W":
                            lon = -lon

                        if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and (lat != 0.0 or lon != 0.0):
                            result["has_gps"] = True
                            result["latitude"] = round(lat, 6)
                            result["longitude"] = round(lon, 6)
            except Exception:
                pass

    except Exception as e:
        result["error"] = str(e)

    return result


def embed_gps_to_image(image: Image.Image, latitude: float, longitude: float, device_name: str = "BBMP Citizen App") -> bytes:
    """
    Injects realistic GPS coordinates and EXIF tags into an in-memory JPEG image using piexif.
    Useful for synthesizing demo test images with verified GPS metadata.
    """
    def _deg_to_dms_rational(deg_float):
        deg = int(abs(deg_float))
        min_float = (abs(deg_float) - deg) * 60
        minutes = int(min_float)
        sec = round((min_float - minutes) * 60 * 100)
        return ((deg, 1), (minutes, 1), (sec, 100))

    lat_dms = _deg_to_dms_rational(latitude)
    lon_dms = _deg_to_dms_rational(longitude)
    lat_ref = "N" if latitude >= 0 else "S"
    lon_ref = "E" if longitude >= 0 else "W"

    now = datetime.now()
    now_str = now.strftime("%Y:%m:%d %H:%M:%S")

    zeroth_ifd = {
        piexif.ImageIFD.Make: device_name.split()[0].encode(),
        piexif.ImageIFD.Model: device_name.encode(),
        piexif.ImageIFD.DateTime: now_str.encode()
    }

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref.encode(),
        piexif.GPSIFD.GPSLatitude: lat_dms,
        piexif.GPSIFD.GPSLongitudeRef: lon_ref.encode(),
        piexif.GPSIFD.GPSLongitude: lon_dms,
        piexif.GPSIFD.GPSDateStamp: now.strftime("%Y:%m:%d").encode(),
        piexif.GPSIFD.GPSTimeStamp: ((now.hour, 1), (now.minute, 1), (now.second, 1))
    }

    exif_dict = {"0th": zeroth_ifd, "Exif": {}, "GPS": gps_ifd, "1st": {}, "thumbnail": None}
    exif_bytes = piexif.dump(exif_dict)

    output = io.BytesIO()
    # Ensure RGB for JPEG
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(output, format="JPEG", exif=exif_bytes, quality=95)
    return output.getvalue()
