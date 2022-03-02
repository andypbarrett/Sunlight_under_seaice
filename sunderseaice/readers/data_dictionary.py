"""Data dictionary for ICESat-2 products relating variables to HDF groups

This include variables I think we need and is not comprehensive
"""

# For each /gtx group
ATL07_DATA_DICT = {
    "delta_time": "sea_ice_segments/delta_time",
    "geoseg_beg": "sea_ice_segments/geoseg_beg",
    "geoseg_end": "sea_ice_segments/geoseg_end",
    "height_segment_id": "sea_ice_segments/height_segment_id",
    "latitude": "sea_ice_segments/latitude",
    "longitude": "sea_ice_segments/longitude",
    "segment_dist_x": "sea_ice_segments/seg_dist_x",
    "across_track_distance": "sea_ice_segments/heights/across_track_distance",
    "height_segment_asr_calc": "sea_ice_segments/heights/height_segment_asr_calc",
    "height_segment_confidence": "sea_ice_segments/heights/height_segment_confidence",
    "height_segment_fit_quality_flag": "sea_ice_segments/heights/height_segment_fit_quality_flag",
    "height_segment_height": "sea_ice_segments/heights/height_segment_height",
    "height_segment_length_seg": "sea_ice_segments/heights/height_segment_length_seg",
    "height_segment_quality": "sea_ice_segments/heights/height_segment_quality",
    "height_segment_rms": "sea_ice_segments/heights/height_segment_rms",
    "height_segment_ssh_flag": "sea_ice_segments/heights/height_segment_ssh_flag",
    "height_segment_surface_error_est": "sea_ice_segments/heights/height_segment_surface_error_est",
    "height_segment_type": "sea_ice_segments/heights/height_segment_type",
    }


# Are in the /gtx group
ATL03_DATA_DICT = {
    "heights": [
        "delta_time",
        "dist_ph_across",
        "dist_ph_along",
        "h_ph",
        "lat_ph",
        "lon_ph",
        "quality_ph",
        "signal_conf_ph",
        ]
    }


# Are in the gtx group
ATL10_DATA_DICT = {
    'freeboard': 'freeboard_beam_segment/beam_freeboard/beam_fb_height',
    'geoseg_beg': 'freeboard_beam_segment/beam_freeboard/geoseg_beg',
    'geoseg_end': 'freeboard_beam_segment/beam_freeboard/geoseg_end',
    'latitude': 'freeboard_beam_segment/beam_freeboard/latitude',
    'longitude': 'freeboard_beam_segment/beam_freeboard/longitude',
    }

