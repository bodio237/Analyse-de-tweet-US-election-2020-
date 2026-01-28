# src/geography_analysis.py

import pandas as pd

class GeographyAnalyzer:
    # Liste des 50 états US + DC
    US_STATES = [
        'ALABAMA','ALASKA','ARIZONA','ARKANSAS','CALIFORNIA','COLORADO','CONNECTICUT',
        'DELAWARE','FLORIDA','GEORGIA','HAWAII','IDAHO','ILLINOIS','INDIANA','IOWA',
        'KANSAS','KENTUCKY','LOUISIANA','MAINE','MARYLAND','MASSACHUSETTS','MICHIGAN',
        'MINNESOTA','MISSISSIPPI','MISSOURI','MONTANA','NEBRASKA','NEVADA','NEW HAMPSHIRE',
        'NEW JERSEY','NEW MEXICO','NEW YORK','NORTH CAROLINA','NORTH DAKOTA','OHIO',
        'OKLAHOMA','OREGON','PENNSYLVANIA','RHODE ISLAND','SOUTH CAROLINA','SOUTH DAKOTA',
        'TENNESSEE','TEXAS','UTAH','VERMONT','VIRGINIA','WASHINGTON','WEST VIRGINIA',
        'WISCONSIN','WYOMING','DISTRICT OF COLUMBIA'
    ]

    def __init__(self, df: pd.DataFrame, candidate_name: str):
        # Copie du dataframe
        self.df = df.copy()
        self.candidate = candidate_name

        # Nettoyage automatique
        self.df['state'] = self.df['state'].astype(str).str.upper()

        # Garder uniquement les états US valides
        self.df = self.df[self.df['state'].isin(self.US_STATES)]

    def tweets_per_state(self, top_n=10) -> pd.Series:
        """
        Retourne le nombre de tweets par État (top N)
        """
        return self.df['state'].value_counts().head(top_n)

    def comparison_with(self, other) -> pd.DataFrame:
        """
        Compare le nombre de tweets par État avec un autre candidat
        """
        df_self = self.df['state'].value_counts()
        df_other = other.df['state'].value_counts()

        comparison = pd.DataFrame({
            self.candidate: df_self,
            other.candidate: df_other
        }).fillna(0).astype(int)

        return comparison