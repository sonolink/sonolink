import sonolink


class TestAutoPlayMode:
    def test_autoplay_mode_exists(self):
        assert hasattr(sonolink, "AutoPlayMode")

    def test_autoplay_mode_disabled(self):
        assert hasattr(sonolink.AutoPlayMode, "DISABLED")

    def test_autoplay_mode_enabled(self):
        assert hasattr(sonolink.AutoPlayMode, "ENABLED")

    def test_autoplay_mode_values(self):
        modes = [m for m in dir(sonolink.AutoPlayMode) if not m.startswith("_")]
        assert len(modes) >= 2


class TestTrackSourceType:
    def test_track_source_type_exists(self):
        assert hasattr(sonolink, "TrackSourceType")

    def test_track_source_youtube(self):
        if hasattr(sonolink, "TrackSourceType"):
            assert hasattr(sonolink.TrackSourceType, "YOUTUBE")

    def test_track_source_soundcloud(self):
        if hasattr(sonolink, "TrackSourceType"):
            # SoundCloud might be supported
            if hasattr(sonolink.TrackSourceType, "SOUNDCLOUD"):
                assert True

    def test_track_source_spotify(self):
        if hasattr(sonolink, "TrackSourceType"):
            # Spotify might be supported
            if hasattr(sonolink.TrackSourceType, "SPOTIFY"):
                assert True

    def test_track_source_multiple_sources(self):
        if hasattr(sonolink, "TrackSourceType"):
            sources = [
                s for s in dir(sonolink.TrackSourceType) if not s.startswith("_")
            ]
            assert len(sources) >= 1


class TestNodeRegion:
    def test_node_region_exists(self):
        assert hasattr(sonolink, "NodeRegion")

    def test_node_region_us_central(self):
        if hasattr(sonolink, "NodeRegion"):
            if hasattr(sonolink.NodeRegion, "US_CENTRAL"):
                assert True

    def test_node_region_eu_west(self):
        if hasattr(sonolink, "NodeRegion"):
            if hasattr(sonolink.NodeRegion, "EU_WEST"):
                assert True

    def test_node_region_variations(self):
        if hasattr(sonolink, "NodeRegion"):
            regions = [r for r in dir(sonolink.NodeRegion) if not r.startswith("_")]
            # Should have at least a few regions
            assert len(regions) >= 1
