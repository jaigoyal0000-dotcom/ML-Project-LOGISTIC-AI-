"""
src/decision_framework.py
-------------------------
FTL vs. Carting Route-Type Decision Framework for Delhivery Logistics.
Quantifies empirical time-cost-SLA trade-offs across distance bands,
departure periods, and hub structural network positions.
"""

import os
import json
import numpy as np
import pandas as pd


class RouteTypeDecisionEngine:
    """
    ML and Data-Backed Decision Framework for selecting between
    Full Truckload (FTL) and Carting routing modes.
    """

    def __init__(self, data_path="data/cleaned_segments.csv", hub_path="data/hub_centrality_metrics.csv"):
        self.data_path = data_path
        self.hub_path = hub_path
        self.df = None
        self.hubs_df = None
        self.comparison_matrix = None

        # Logistics Cost Parameters (INR calibrated to Indian freight industry standards)
        self.COST_FTL_PER_KM = 38.0        # ₹38/km dedicated vehicle linehaul
        self.COST_CARTING_PER_KM = 22.0    # ₹22/km shared consolidated freight
        self.COST_CARTING_DWELL = 350.0    # ₹350 per-hop sorting and dwell handling overhead
        self.SLA_BREACH_PENALTY = 1200.0   # ₹1,200 contractual SLA penalty / expedited recovery

    def load_and_merge(self):
        print("Loading data for FTL vs. Carting decision framework...")
        self.df = pd.read_csv(self.data_path)
        self.hubs_df = pd.read_csv(self.hub_path)

        # Merge hub chokepoint tier
        hub_risk = self.hubs_df[['hub_id', 'chokepoint_risk_score', 'betweenness_centrality']].copy()
        hub_risk['hub_risk_tier'] = pd.qcut(
            hub_risk['chokepoint_risk_score'],
            q=[0, 0.5, 0.85, 1.0],
            labels=['Low Hub Risk', 'Moderate Hub Risk', 'High Chokepoint Hub']
        )
        self.df = self.df.merge(hub_risk, left_on='source_center', right_on='hub_id', how='left')
        self.df['hub_risk_tier'] = self.df['hub_risk_tier'].fillna('Moderate Hub Risk')

    def analyze_tradeoffs(self):
        """
        Quantifies empirical delivery time, delay ratios, and SLA breach rates
        stratified by Route Type, Distance Band, and Hub Risk Tier.
        """
        print("Evaluating empirical route-type performance trade-offs...")
        grouped = self.df.groupby(['distance_band', 'hub_risk_tier', 'route_type']).agg(
            trip_count=('trip_uuid', 'count'),
            median_actual_hr=('actual_time_hr', 'median'),
            median_osrm_hr=('osrm_time_hr', 'median'),
            median_delay_ratio=('delay_ratio', 'median'),
            sla_breach_rate=('sla_breached', 'mean'),
            avg_distance_km=('actual_distance_km', 'mean')
        ).reset_index()

        # Compute Economic Cost Model
        def compute_cost(row):
            dist = row['avg_distance_km']
            breach_prob = row['sla_breach_rate']
            if row['route_type'] == 'FTL':
                base_cost = dist * self.COST_FTL_PER_KM
            else:
                base_cost = (dist * self.COST_CARTING_PER_KM) + self.COST_CARTING_DWELL
            expected_penalty = breach_prob * self.SLA_BREACH_PENALTY
            total_cost = base_cost + expected_penalty
            return pd.Series([round(base_cost, 1), round(expected_penalty, 1), round(total_cost, 1)])

        grouped[['base_cost_inr', 'expected_sla_penalty_inr', 'total_economic_cost_inr']] = grouped.apply(compute_cost, axis=1)

        self.comparison_matrix = grouped
        return grouped

    def build_recommendation_rules(self):
        """
        Derives an operational recommendation rule table for logistics planners.
        """
        pivot = self.comparison_matrix.pivot(
            index=['distance_band', 'hub_risk_tier'],
            columns='route_type',
            values=['median_actual_hr', 'sla_breach_rate', 'total_economic_cost_inr']
        )
        pivot.columns = [f"{col[0]}_{col[1]}" for col in pivot.columns]
        pivot = pivot.reset_index()

        rules = []
        for _, row in pivot.iterrows():
            band = row['distance_band']
            tier = row['hub_risk_tier']
            ftl_time = row['median_actual_hr_FTL']
            cart_time = row['median_actual_hr_Carting']
            ftl_sla = row['sla_breach_rate_FTL']
            cart_sla = row['sla_breach_rate_Carting']
            ftl_cost = row['total_economic_cost_inr_FTL']
            cart_cost = row['total_economic_cost_inr_Carting']

            time_diff = cart_time - ftl_time # positive means Carting is slower
            cost_saving_carting = ftl_cost - cart_cost # positive means Carting is cheaper

            if "High Chokepoint" in str(tier) or "Long" in str(band):
                recommendation = "FTL (Dedicated)"
                rationale = "High structural network risk or long corridor: FTL eliminates intermediate sorting congestion and protects SLA."
            elif cost_saving_carting > 500 and (cart_sla - ftl_sla < 0.05):
                recommendation = "Carting (Consolidated)"
                rationale = f"Significant economic advantage (INR {cost_saving_carting:.0f} savings) with comparable SLA reliability."
            else:
                if ftl_cost <= cart_cost * 1.15:
                    recommendation = "FTL (Preferred)"
                    rationale = "Cost delta is narrow, but FTL provides faster turnaround and superior predictability."
                else:
                    recommendation = "Carting (Standard)"
                    rationale = "Economical consolidation optimal for non-critical shipments."

            rules.append({
                'Distance Band': band,
                'Source Hub Risk': tier,
                'FTL Median Time (hr)': round(ftl_time, 2),
                'Carting Median Time (hr)': round(cart_time, 2),
                'Time Delta (Carting - FTL)': round(time_diff, 2),
                'FTL SLA Breach %': round(ftl_sla * 100, 1),
                'Carting SLA Breach %': round(cart_sla * 100, 1),
                'FTL Total Cost (INR)': round(ftl_cost, 0),
                'Carting Total Cost (INR)': round(cart_cost, 0),
                'Recommended Mode': recommendation,
                'Operational Rationale': rationale
            })

        rules_df = pd.DataFrame(rules)
        return rules_df

    def recommend(self, distance_km, source_hub_id, is_time_critical=False):
        """Interactive route-type recommender function."""
        # Find hub risk score
        hub_match = self.hubs_df[self.hubs_df['hub_id'] == source_hub_id]
        if not hub_match.empty:
            choke_score = hub_match.iloc[0]['chokepoint_risk_score']
            bc = hub_match.iloc[0]['betweenness_centrality']
        else:
            choke_score = 25.0
            bc = 0.01

        # Distance band
        if distance_km < 100:
            dist_band = "Short (<100km)"
        elif distance_km <= 300:
            dist_band = "Medium (100-300km)"
        else:
            dist_band = "Long (>300km)"

        # Operational logic
        if is_time_critical or choke_score > 60.0 or distance_km > 300:
            rec = "FTL"
            reason = f"Shipment travels from high-chokepoint hub ({choke_score:.1f}) or long haul ({distance_km:.1f} km). FTL bypasses intermediate dwell delays."
        else:
            rec = "Carting"
            est_save = (distance_km * (self.COST_FTL_PER_KM - self.COST_CARTING_PER_KM)) - self.COST_CARTING_DWELL
            reason = f"Short/medium haul from low-risk facility. Carting saves an estimated INR {max(0, est_save):.0f} per trip."

        return {
            'recommended_route_type': rec,
            'distance_km': distance_km,
            'distance_band': dist_band,
            'source_hub_chokepoint_score': choke_score,
            'is_time_critical': is_time_critical,
            'operational_rationale': reason
        }

    def save_framework_artifacts(self, output_dir="data"):
        os.makedirs(output_dir, exist_ok=True)
        rules_df = self.build_recommendation_rules()
        rules_csv = os.path.join(output_dir, "ftl_vs_carting_rules.csv")
        rules_df.to_csv(rules_csv, index=False)
        print(f"Saved route decision rules to {rules_csv}")
        return rules_df


def run_decision_framework():
    engine = RouteTypeDecisionEngine()
    engine.load_and_merge()
    engine.analyze_tradeoffs()
    rules = engine.save_framework_artifacts()
    print("\n=== FTL vs. CARTING DECISION MATRIX ===")
    print(rules[['Distance Band', 'Source Hub Risk', 'Recommended Mode', 'FTL Total Cost (INR)', 'Carting Total Cost (INR)']].to_string(index=False))
    return engine


if __name__ == "__main__":
    run_decision_framework()
