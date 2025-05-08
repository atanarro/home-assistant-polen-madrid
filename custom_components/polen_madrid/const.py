"""Constants for the Polen Madrid integration."""
from datetime import timedelta

DOMAIN = "polen_madrid"

CONF_STATIONS = "stations"

API_URL = (
    'https://idem.comunidad.madrid/geoserver3/wfs?version=2.0.0&request=GetFeature'
    '&typeName=SPOL_V_CAPTADORES_GIS'
)
API_HEADERS = {
    "accept": "*/*",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "pragma": "no-cache",
}
API_DATA_PAYLOAD = (
    'SRS=EPSG%3A25830&outputFormat=application%2Fjson&Filter=%3CFilter%20xmlns'
    '%3Agml%3D%22http%3A%2F%2Fwww.opengis.net%2Fgml%22%3E%3CIntersects%3E%3CPropertyName%3E'
    'GEOMETRY1%3C%2FPropertyName%3E%3Cgml%3APolygon%20srsName%3D%22urn%3Ax-ogc%3Adef%3Acrs'
    '%3AEPSG%3A25830%22%3E%3Cexterior%3E%3CLinearRing%3E%3CposList%20srsDimension%3D%222%22%3E'
    '450672.7187693954%204558092.8707015915%20361394.26973231026%204458418.985817723%20'
    '450061.222543114%204423869.449032824%20496229.18762736%204440379.847142422%20'
    '458316.4215979129%204514370.890522472%20467488.864992134%204544945.701836541%20'
    '450672.7187693954%204558092.8707015915%3C%2FposList%3E%3C%2FLinearRing%3E%3C%2Fexterior%3E'
    '%3C%2Fgml%3APolygon%3E%3C%2FIntersects%3E%3C%2FFilter%3E'
)

FIELD_MAPPING = {
    "NM_ID_CAPTADORES": "station_id",
    "CD_CAPTADORES": "station_code",
    "DS_NOMBRE": "location_name",
    "NM_LONGITUD": "longitude_utm",
    "NM_LATITUD": "latitude_utm",
    "NM_ALTITUD": "altitude",
    "NM_ALTURA": "sensor_height",
    "FC_FECHA_MEDICION": "measurement_date",
    "NM_VALOR": "pollen_value",
    "CD_MATERIAS": "pollen_code",
    "DS_MATERIAS": "pollen_type",
    "NM_ALTO": "high_threshold",
    "NM_MEDIO": "medium_threshold",
    "NM_MUYALTO": "very_high_threshold",
    "coordinates": "coordinates_utm"
}

SCAN_INTERVAL = timedelta(hours=1)

POLLUTANT_MAPPING = {
    "NO2": "Nitrogen Dioxide (NO2)",
    "PM2_5": "Particulate Matter < 2.5μm (PM2.5)"
}
