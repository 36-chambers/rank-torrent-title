from typing import Any
from unittest import TestCase

import PTN

from RTN import Rank, RankingConfig, rank_items


class SortItems(TestCase):
    def test_sorts(self):
        items: list[dict[str, Any]] = [
            PTN.parse(item, coherent_types=True)
            for item in [
                "Movie.720p.mkv",
                "Movie.1080p.mkv",
                "Movie.1080p.Extended.mkv",
                "Movie.mkv",
                "Movie.2160p.mkv",
            ]
        ]
        config = RankingConfig(
            rankings=[
                Rank(name="resolution", preference=["1080p", "720p"]),
                Rank(name="extended", preference=[True]),
            ]
        )
        result = rank_items(items, config)
        self.assertEqual(
            result,
            [
                PTN.parse(item, coherent_types=True)
                for item in [
                    "Movie.1080p.Extended.mkv",
                    "Movie.1080p.mkv",
                    "Movie.720p.mkv",
                    "Movie.mkv",
                    "Movie.2160p.mkv",
                ]
            ],
        )

    def test_excludes_required_mismatches(self):
        self.maxDiff = None
        items: list[dict[str, Any]] = [
            PTN.parse(item, coherent_types=True)
            for item in [
                "Movie.720p.DDP51.x265.mkv",
                "Movie.1080p.BluRay.mkv",
                "Movie.BluRay.mkv",
                "Movie.Extended.2160p.DDP51.mkv",
            ]
        ]
        config = RankingConfig(
            rankings=[
                Rank(name="resolution", preference=["1080p", "2160p", "720p"]),
                Rank(name="audio", require="*5.1"),
            ]
        )
        result = rank_items(items, config)
        self.assertEqual(
            result,
            [
                PTN.parse(item, coherent_types=True)
                for item in [
                    "Movie.Extended.2160p.DDP51.mkv",
                    "Movie.720p.DDP51.x265.mkv",
                ]
            ],
        )

    def test_excludes_exclude_matches(self):
        self.maxDiff = None
        items: list[dict[str, Any]] = [
            PTN.parse(item, coherent_types=True)
            for item in [
                "Movie.720p.DDP51.x265.mkv",
                "Movie.1080p.BluRay.mkv",
                "Movie.BluRay.AAC2.720p.mkv",
                "Movie.Extended.2160p.DDP51.mkv",
            ]
        ]
        config = RankingConfig(
            rankings=[
                Rank(name="resolution", preference=["1080p", "2160p", "720p"]),
                Rank(name="audio", exclude=["Dolby Digital*"]),
            ]
        )
        result = rank_items(items, config)
        self.assertEqual(
            result,
            [
                PTN.parse(item, coherent_types=True)
                for item in [
                    "Movie.1080p.BluRay.mkv",
                    "Movie.BluRay.AAC2.720p.mkv",
                ]
            ],
        )

    def test_sorts_precedence(self):
        self.maxDiff = None
        items: list[dict[str, Any]] = [
            PTN.parse(item, coherent_types=True)
            for item in [
                "Lord.of.the.Rings.Return.of.King.2003.EXTENDED.1080p.BluRay.HEVC",
                "The Lord of the Rings: The Return of the King 2003 EXTENDED 10bit 1080p BluRay",
                "The Lord of the Rings: The Return of the King 2003 EXTENDED 10bit HDR 1080p BluRay",
                "The Lord of the Rings: The Return of the King (2003) 2160p AV1 HDR10 EN/FR/ES/DE/ITA AC3 5.1-UH",
                "The Lord of the Rings: The Return of the King 2003 2160p 10bit x265 BluRay",
                "The Lord of the Rings: The Return of the King [2003] 2160p HDR Bluray AV1 Opus Multi6",
                "The Lord of the Rings: The Return of the King 2003 EXTENDED 720p BluRay",
                "The.Lord.of.the.Rings.The.Return.of.the.King.2003.Extended.2160p.UHD.HDR.BluRay.x265.10bit.TRUEHD.ATMOS.[WMAN-LorD]",
                "The Lord of the Rings: The Return of the King THEATRICAL EDITION",
                "Trilogie.Le.Seigneur.Des.Anneaux.Version.Longue.DVDRIP.TRUEFRENCH.SUBFORCED.XVID.AC3-KDLN",
            ]
        ]
        config = RankingConfig(
            rankings=[
                Rank(name="resolution", preference=["1080p", "2160p", "720p"]),
                Rank(name="extended", require=True),
                Rank(name="audio", preference=["*5.1", "*7.1"]),
                Rank(name="bitDepth", preference=["10"]),
                Rank(name="hdr", preference=[True]),
            ]
        )
        result = rank_items(items, config)
        self.assertEqual(
            result,
            [
                PTN.parse(item, coherent_types=True)
                for item in [
                    "The Lord of the Rings: The Return of the King 2003 EXTENDED 10bit HDR 1080p BluRay",
                    "The Lord of the Rings: The Return of the King 2003 EXTENDED 10bit 1080p BluRay",
                    "Lord.of.the.Rings.Return.of.King.2003.EXTENDED.1080p.BluRay.HEVC",
                    "The.Lord.of.the.Rings.The.Return.of.the.King.2003.Extended.2160p.UHD.HDR.BluRay.x265.10bit.TRUEHD.ATMOS.[WMAN-LorD]",
                    "The Lord of the Rings: The Return of the King 2003 EXTENDED 720p BluRay",
                ]
            ],
        )
