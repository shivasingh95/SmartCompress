"""
Bandwidth Simulator Module
Simulates real-world streaming and download times across network types.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class NetworkProfile:
    name: str
    emoji: str
    speed_mbps: float
    typical_use: str


NETWORK_PROFILES: List[NetworkProfile] = [
    NetworkProfile("2G EDGE",    "🐢", 0.1,   "Rural / legacy mobile"),
    NetworkProfile("3G HSPA",    "📶", 2.0,   "Basic mobile / developing regions"),
    NetworkProfile("4G LTE",     "📱", 20.0,  "Standard mobile connection"),
    NetworkProfile("Cable/DSL",  "🏠", 50.0,  "Home broadband"),
    NetworkProfile("5G",         "⚡", 200.0, "Urban mobile / modern"),
    NetworkProfile("Fiber",      "🚀", 1000.0,"Premium home / office"),
]


class BandwidthSimulator:
    """
    Computes streaming and download time estimates across real-world networks.
    Also calculates monthly CDN cost savings from compression.
    """

    CDN_COST_PER_GB = 0.085  # USD per GB (AWS CloudFront US pricing approx.)
    MONTHLY_DELIVERIES = 10_000  # assumed deliveries for cost projection

    def simulate(self, original_bytes: int, compressed_bytes: int) -> dict:
        """
        Run full bandwidth simulation for both original and compressed sizes.

        Returns:
            dict with per-network download times and CDN cost analysis.
        """
        original_mb = original_bytes / (1024 ** 2)
        compressed_mb = compressed_bytes / (1024 ** 2)

        network_data = []
        for profile in NETWORK_PROFILES:
            orig_s = self._download_time(original_mb, profile.speed_mbps)
            comp_s = self._download_time(compressed_mb, profile.speed_mbps)
            saved_s = orig_s - comp_s
            saving_pct = round((saved_s / orig_s * 100), 1) if orig_s > 0 else 0

            network_data.append({
                "network": profile.name,
                "emoji": profile.emoji,
                "speed": f"{profile.speed_mbps} Mbps",
                "typical_use": profile.typical_use,
                "original_time": self._format_time(orig_s),
                "compressed_time": self._format_time(comp_s),
                "time_saved": self._format_time(saved_s),
                "saving_pct": saving_pct,
                "original_sec": orig_s,
                "compressed_sec": comp_s,
            })

        cdn_analysis = self._cdn_cost_analysis(original_bytes, compressed_bytes)

        return {
            "original_mb": round(original_mb, 3),
            "compressed_mb": round(compressed_mb, 3),
            "networks": network_data,
            "cdn": cdn_analysis,
        }

    # ── Private ────────────────────────────────────────────────────────────────

    def _download_time(self, size_mb: float, speed_mbps: float) -> float:
        if speed_mbps <= 0:
            return float("inf")
        return size_mb / speed_mbps * 8  # MB ÷ Mbps × 8 bits/byte = seconds

    def _format_time(self, seconds: float) -> str:
        if seconds >= 3600:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"
        elif seconds >= 60:
            m = int(seconds // 60)
            s = int(seconds % 60)
            return f"{m}m {s}s"
        elif seconds >= 1:
            return f"{seconds:.1f}s"
        else:
            return f"{seconds * 1000:.0f}ms"

    def _cdn_cost_analysis(self, original_bytes: int, compressed_bytes: int) -> dict:
        orig_gb = original_bytes / (1024 ** 3)
        comp_gb = compressed_bytes / (1024 ** 3)

        monthly_orig_cost = orig_gb * self.MONTHLY_DELIVERIES * self.CDN_COST_PER_GB
        monthly_comp_cost = comp_gb * self.MONTHLY_DELIVERIES * self.CDN_COST_PER_GB
        monthly_saving = monthly_orig_cost - monthly_comp_cost
        annual_saving = monthly_saving * 12

        return {
            "monthly_original_usd": round(monthly_orig_cost, 2),
            "monthly_compressed_usd": round(monthly_comp_cost, 2),
            "monthly_saving_usd": round(monthly_saving, 2),
            "annual_saving_usd": round(annual_saving, 2),
            "deliveries_assumed": self.MONTHLY_DELIVERIES,
        }
