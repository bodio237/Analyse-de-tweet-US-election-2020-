from __future__ import annotations

import re
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class LocationCleaner:
    """Low-level cleaning of free-text locations."""
    def clean(self, text) -> str | None:
        if pd.isna(text):
            return None
        s = str(text).lower()
        s = re.sub(r"[^a-zA-Z\s]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s if s else None


@dataclass
class CountryNormalizer:
    """
    Rule-based mapping from noisy user_location to a country label.
    """
    def to_country(self, loc: str | None) -> str:
        if not isinstance(loc, str) or not loc:
            return "Other"

        s = loc.lower()

        # United States
        if "united states" in s or " usa" in s or s.endswith(" usa") or "america" in s or "u.s." in s:
            return "United States"

        # United Kingdom
        if "united kingdom" in s or " uk" in s or "england" in s or "london" in s or "scotland" in s:
            return "United Kingdom"

        # India
        if "india" in s or "delhi" in s or "mumbai" in s:
            return "India"

        # France
        if "france" in s or "paris" in s:
            return "France"

        # Canada
        if "canada" in s or "toronto" in s:
            return "Canada"

        # Germany
        if "deutschland" in s or "germany" in s or "berlin" in s:
            return "Germany"

        # Italy
        if "italia" in s or "italy" in s or "rome" in s:
            return "Italy"

        # Australia
        if "australia" in s or "sydney" in s or "melbourne" in s:
            return "Australia"

        # Mexico
        if "mexico" in s or "mxico" in s:
            return "Mexico"

        # Turkey
        if "turkiye" in s or "turkey" in s or "istanbul" in s:
            return "Turkey"

        return "Other"


@dataclass
class GeographyAnalyzer:
    """
    OOP geographic analysis:
    - load(): robust CSV loading
    - compare(): counts by cleaned user_location (Biden vs Trump)
    - aggregate_by_country(): country-level aggregation for world map
    """
    sep: str = ";"
    encoding: str = "utf-8"

    # ✅ IMPORTANT: use default_factory (dataclass-safe)
    cleaner: LocationCleaner = field(default_factory=LocationCleaner)
    normalizer: CountryNormalizer = field(default_factory=CountryNormalizer)

    def load(self, path: str) -> pd.DataFrame:
        return pd.read_csv(
            path,
            sep=self.sep,
            dtype=str,
            encoding=self.encoding,
            low_memory=False,
            on_bad_lines="skip"
        )

    @staticmethod
    def find_location_column(df: pd.DataFrame) -> str:
        for col in df.columns:
            if "location" in col.lower():
                return col
        raise ValueError("No location column found")

    def _locations_series(self, df: pd.DataFrame) -> pd.Series:
        loc_col = self.find_location_column(df)
        return df[loc_col].apply(self.cleaner.clean)

    def compare(self, biden_df: pd.DataFrame, trump_df: pd.DataFrame) -> pd.DataFrame:
        biden_locs = self._locations_series(biden_df).dropna()
        trump_locs = self._locations_series(trump_df).dropna()

        biden_counts = biden_locs.value_counts()
        trump_counts = trump_locs.value_counts()

        comparison = pd.DataFrame({"Biden": biden_counts, "Trump": trump_counts}).fillna(0)
        comparison["diff"] = comparison["Biden"] - comparison["Trump"]
        comparison["total"] = comparison["Biden"] + comparison["Trump"]

        return comparison.reset_index().rename(columns={"index": "user_location"})

    def aggregate_by_country(self, geo_clean: pd.DataFrame) -> pd.DataFrame:
        """
        Takes compare() output (geo_clean with user_location, Biden, Trump...)
        and produces a country-level aggregation.
        """
        df = geo_clean.copy()
        df["country"] = df["user_location"].apply(self.normalizer.to_country)

        geo_country = df.groupby("country", as_index=False)[["Biden", "Trump"]].sum()
        return geo_country


# ---- Backward compatibility (if older notebook code still imports these)
def load_twitter_csv(path: str) -> pd.DataFrame:
    return GeographyAnalyzer().load(path)

def compare_candidates(biden_df: pd.DataFrame, trump_df: pd.DataFrame) -> pd.DataFrame:
    return GeographyAnalyzer().compare(biden_df, trump_df)