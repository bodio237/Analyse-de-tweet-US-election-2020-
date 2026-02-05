from __future__ import annotations
import numpy as np
import folium
import branca.colormap as cm
from branca.element import MacroElement
from jinja2 import Template

class WorldMapBuilder:
    """Build the world dominance map with a double legend (Biden/Trump)."""

    def __init__(self, tiles="cartodbpositron", levels=22):
        self.tiles = tiles
        self.levels = levels

    @staticmethod
    def compute_rel_diff(df, biden_col="Biden", trump_col="Trump"):
        out = df.copy()
        denom = (out[biden_col] + out[trump_col]).replace(0, np.nan)
        out["rel_diff"] = (out[biden_col] - out[trump_col]) / denom
        return out

    @staticmethod
    def add_double_legend(m: folium.Map, max_abs: float) -> None:
        legend = MacroElement()
        legend._template = Template(f"""
        {{% macro html(this, kwargs) %}}
        <div style="
            position: fixed; top: 10px; right: 10px; z-index: 9999;
            background: white; padding: 10px 12px;
            border: 2px solid rgba(0,0,0,0.2); border-radius: 6px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.2);
            font-family: Arial, sans-serif; font-size: 12px; width: 270px;">
          <div style="font-weight:700; margin-bottom:8px;">
            Relative dominance (Biden − Trump) / (Biden + Trump)
          </div>

          <div style="margin-bottom:10px;">
            <div style="font-weight:700; margin-bottom:4px; color:#1f77b4;">Biden (positive)</div>
            <div style="height:14px; background:linear-gradient(to right,#deebf7,#08519c);
                        border:1px solid #999; border-radius:3px;"></div>
            <div style="display:flex; justify-content:space-between; margin-top:3px;">
              <span>0</span><span>+{max_abs:.2f}</span>
            </div>
          </div>

          <div>
            <div style="font-weight:700; margin-bottom:4px; color:#d62728;">Trump (negative)</div>
            <div style="height:14px; background:linear-gradient(to right,#fee0d2,#a50f15);
                        border:1px solid #999; border-radius:3px;"></div>
            <div style="display:flex; justify-content:space-between; margin-top:3px;">
              <span>-{max_abs:.2f}</span><span>0</span>
            </div>
          </div>

          <div style="margin-top:10px; font-size:11px; color:#444;">
            Blue = Biden dominant • Red = Trump dominant
          </div>
        </div>
        {{% endmacro %}}
        """)
        m.get_root().add_child(legend)

    def build(self, countries_geo: dict, value_by_country: dict) -> folium.Map:
        m = folium.Map(location=[20, 0], zoom_start=2, tiles=self.tiles)

        vals = [v for v in value_by_country.values()
                if v is not None and not (isinstance(v, float) and np.isnan(v))]
        max_abs = float(np.nanmax(np.abs(vals))) if vals else 1.0
        max_abs = max(max_abs, 1e-6)

        bins = np.linspace(-max_abs, max_abs, self.levels + 1)
        linear = cm.LinearColormap(["red", "white", "blue"], vmin=-max_abs, vmax=max_abs)
        step_cm = linear.to_step(index=bins)

        def style_function(feature):
            name = feature["properties"].get("name")
            val = value_by_country.get(name, None)

            if val is None or (isinstance(val, float) and np.isnan(val)):
                return {"fillOpacity": 0.05, "weight": 0.3, "color": "#999999", "fillColor": "#ffffff"}

            return {"fillOpacity": 0.85, "weight": 0.4, "color": "#666666", "fillColor": step_cm(val)}

        def highlight_function(feature):
            return {"weight": 2, "color": "#000000"}

        folium.GeoJson(
            countries_geo,
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Country:"], sticky=True),
            name="Dominance map"
        ).add_to(m)

        self.add_double_legend(m, max_abs)
        return m