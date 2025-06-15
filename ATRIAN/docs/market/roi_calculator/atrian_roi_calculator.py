#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRiAN Ethics ROI Calculator
============================

This module implements the ATRiAN Ethics ROI Calculation Methodology to quantify
the return on investment for implementing ethical AI systems using ATRiAN.

The calculator evaluates investment returns across five key dimensions:
1. Risk Mitigation: Value of avoiding ethical failures and associated costs
2. Operational Efficiency: Streamlining ethical review processes and decision-making
3. Brand Value: Enhancing reputation and customer trust
4. Regulatory Compliance: Reducing compliance costs and penalties
5. Innovation Enablement: Accelerating development while maintaining ethical standards

Usage:
    1. Instantiate the ATRiANROICalculator with organization parameters
    2. Set specific input values for each benefit dimension
    3. Calculate ROI and generate reports

Example:
    calculator = ATRiANROICalculator(
        organization_name="Example Corp",
        industry="Financial Services",
        time_horizon=3,
        discount_rate=0.1
    )
    calculator.set_implementation_costs(150000)
    calculator.set_annual_costs(50000)
    calculator.calculate_roi()
    calculator.generate_report("roi_report.pdf")

Created: 2025-06-02
Author: EGOS Team
Version: 0.1.0
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import math
import json
import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field

# Constants for industry-specific adjustments
INDUSTRY_MULTIPLIERS = {
    "Financial Services": {"risk": 1.5, "compliance": 1.0, "brand": 0.8},
    "Healthcare": {"risk": 1.7, "compliance": 1.0, "brand": 1.0},
    "Retail": {"risk": 1.0, "compliance": 0.7, "brand": 1.2},
    "Manufacturing": {"risk": 0.8, "compliance": 0.7, "brand": 0.6},
    "Government": {"risk": 1.3, "compliance": 1.2, "brand": 0.8},
    "Technology": {"risk": 1.2, "compliance": 0.8, "brand": 1.1},
    "Other": {"risk": 1.0, "compliance": 0.8, "brand": 0.9}
}

# Default values for sensitivity analysis
DEFAULT_VARIANCE = {
    "risk_mitigation": 0.3,        # 30% variance in risk estimates
    "operational_efficiency": 0.25, # 25% variance in efficiency estimates
    "brand_value": 0.4,            # 40% variance in brand impact
    "regulatory_compliance": 0.3,   # 30% variance in compliance benefits
    "innovation_enablement": 0.35,  # 35% variance in innovation estimates
    "costs": 0.2                    # 20% variance in cost estimates
}

@dataclass
class ROIInputs:
    """Class for storing ROI calculation inputs."""
    # Organization profile
    organization_name: str
    industry: str
    time_horizon: int = 3
    discount_rate: float = 0.1
    
    # Implementation costs
    implementation_cost: float = 0
    annual_cost: float = 0
    
    # Risk mitigation inputs
    incident_probability: float = 0
    incident_cost: float = 0
    risk_reduction_factor: float = 0.6
    bias_impact_value: float = 0
    
    # Operational efficiency inputs
    reviews_per_year: int = 0
    hours_per_review: float = 0
    efficiency_gain: float = 0.5
    hourly_rate: float = 0
    projects_per_year: int = 0
    average_delay_cost: float = 0
    delay_reduction_factor: float = 0.3
    
    # Brand value inputs
    brand_value: float = 0
    ethics_premium_factor: float = 0.01
    customers: int = 0
    revenue_per_customer: float = 0
    trust_factor: float = 0.5
    conversion_impact: float = 0.02
    
    # Regulatory compliance inputs
    annual_compliance_costs: float = 0
    efficiency_factor: float = 0.3
    penalty_probability: float = 0
    average_penalty_cost: float = 0
    compliance_risk_reduction: float = 0.6
    
    # Innovation enablement inputs
    innovation_value: float = 0
    acceleration_factor: float = 0.15
    ethical_market_opportunity: float = 0
    ethical_barrier_factor: float = 0.5
    expected_market_share: float = 0

@dataclass
class ROIResults:
    """Class for storing ROI calculation results."""
    # NPV values
    npv_benefits: float = 0
    npv_costs: float = 0
    net_benefits: float = 0
    
    # ROI metrics
    roi_percentage: float = 0
    payback_period_months: float = 0
    
    # Benefit breakdown
    risk_mitigation_benefits: float = 0
    operational_efficiency_benefits: float = 0
    brand_value_benefits: float = 0
    regulatory_compliance_benefits: float = 0
    innovation_enablement_benefits: float = 0
    
    # Sensitivity analysis
    best_case_roi: float = 0
    worst_case_roi: float = 0
    confidence_interval: Tuple[float, float] = field(default_factory=lambda: (0, 0))
    
    # Yearly breakdown
    yearly_benefits: List[float] = field(default_factory=list)
    yearly_costs: List[float] = field(default_factory=list)
    cumulative_net_benefits: List[float] = field(default_factory=list)

class ATRiANROICalculator:
    """
    Main calculator class for ATRiAN Ethics ROI assessment.
    
    This class implements the full ROI calculation methodology and provides
    methods for setting inputs, calculating benefits, and generating reports.
    """
    
    def __init__(self, organization_name: str, industry: str, 
                 time_horizon: int = 3, discount_rate: float = 0.1):
        """
        Initialize the ROI calculator with organization parameters.
        
        Args:
            organization_name: Name of the organization
            industry: Industry sector (must match keys in INDUSTRY_MULTIPLIERS)
            time_horizon: Number of years for ROI calculation (default: 3)
            discount_rate: Annual discount rate for NPV calculations (default: 0.1)
        """
        self.inputs = ROIInputs(
            organization_name=organization_name,
            industry=industry if industry in INDUSTRY_MULTIPLIERS else "Other",
            time_horizon=time_horizon,
            discount_rate=discount_rate
        )
        
        self.results = ROIResults()
        self.industry_multipliers = INDUSTRY_MULTIPLIERS[self.inputs.industry]
        self.calculation_date = datetime.datetime.now()
        
    def set_implementation_costs(self, implementation_cost: float) -> None:
        """
        Set the one-time implementation costs for ATRiAN.
        
        Args:
            implementation_cost: Total one-time costs including licensing, 
                                 integration, training, customization, and infrastructure.
        """
        self.inputs.implementation_cost = implementation_cost
        
    def set_annual_costs(self, annual_cost: float) -> None:
        """
        Set the recurring annual costs for ATRiAN.
        
        Args:
            annual_cost: Annual recurring costs including subscription, 
                         maintenance, usage, support, and periodic training.
        """
        self.inputs.annual_cost = annual_cost
        
    def _calculate_npv(self, cash_flows: List[float]) -> float:
        """
        Calculate the Net Present Value of a series of cash flows.
        
        Args:
            cash_flows: List of cash flows, starting with year 0
                        (typically negative for initial investment)
        
        Returns:
            The net present value of the cash flows
        """
        npv = 0
        for year, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + self.inputs.discount_rate) ** year)
        return npv
    
    def _calculate_total_costs(self) -> List[float]:
        """
        Calculate the total costs over the time horizon.
        
        Returns:
            List of costs for each year, starting with year 0
        """
        costs = [self.inputs.implementation_cost]  # Year 0 (implementation)
        
        # Add annual costs for years 1 to time_horizon
        for _ in range(1, self.inputs.time_horizon + 1):
            costs.append(self.inputs.annual_cost)
            
        return costs
    
    def _calculate_payback_period(self, cumulative_net_benefits: List[float]) -> float:
        """
        Calculate the payback period in months.
        
        Args:
            cumulative_net_benefits: List of cumulative net benefits by year
        
        Returns:
            Payback period in months, or math.inf if no payback within time horizon
        """
        # If never reaching positive, return infinity
        if all(benefit < 0 for benefit in cumulative_net_benefits):
            return math.inf
        
        # Find the first year with positive cumulative benefit
        for i, benefit in enumerate(cumulative_net_benefits):
            if benefit >= 0:
                if i == 0:  # Payback in less than a year
                    previous_benefit = -self.inputs.implementation_cost
                    # Linear interpolation to find months
                    percentage_of_year = abs(previous_benefit) / (abs(previous_benefit) + benefit)
                    return percentage_of_year * 12
                else:
                    previous_benefit = cumulative_net_benefits[i-1]
                    # Linear interpolation to find months
                    percentage_of_year = abs(previous_benefit) / (abs(previous_benefit) + benefit)
                    return (i - 1) * 12 + percentage_of_year * 12
        
        return math.inf  # Should not reach here if any benefit is positive
    
    # ------ Risk Mitigation Benefit Methods ------
    
    def set_risk_mitigation_inputs(self, incident_probability: float, incident_cost: float, 
                                risk_reduction_factor: float = 0.6, bias_impact_value: float = 0) -> None:
        """
        Set inputs for risk mitigation benefits calculation.
        
        Args:
            incident_probability: Annual probability (0-1) of an ethical incident
            incident_cost: Average cost of an incident in currency units
            risk_reduction_factor: Estimated reduction in risk (0-1) from ATRiAN implementation
            bias_impact_value: Economic impact of algorithmic bias in currency units
        """
        self.inputs.incident_probability = incident_probability
        self.inputs.incident_cost = incident_cost
        self.inputs.risk_reduction_factor = risk_reduction_factor
        self.inputs.bias_impact_value = bias_impact_value
    
    def _calculate_risk_mitigation_benefits(self) -> float:
        """
        Calculate the NPV of risk mitigation benefits.
        
        Returns:
            NPV of risk mitigation benefits
        """
        # Apply industry-specific risk multiplier
        risk_multiplier = self.industry_multipliers["risk"]
        
        # Incident avoidance benefit calculation
        incident_avoidance = self.inputs.incident_probability * self.inputs.incident_cost * \
                            self.inputs.risk_reduction_factor * risk_multiplier
        
        # Bias reduction benefit calculation
        bias_reduction = self.inputs.bias_impact_value * self.inputs.risk_reduction_factor * risk_multiplier
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        for _ in range(1, self.inputs.time_horizon + 1):
            yearly_benefits.append(incident_avoidance + bias_reduction)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Brand Value Benefit Methods ------
    
    def set_brand_value_inputs(self, brand_value: float, ethics_premium_factor: float = 0.01,
                          customers: int = 0, revenue_per_customer: float = 0,
                          trust_factor: float = 0.5, conversion_impact: float = 0.02) -> None:
        """
        Set inputs for brand value benefits calculation.
        
        Args:
            brand_value: Estimated total brand value in currency units
            ethics_premium_factor: Incremental value from ethical AI positioning (0-1)
            customers: Number of customers/users
            revenue_per_customer: Annual revenue per customer in currency units
            trust_factor: Impact of ethical practices on trust (0-1)
            conversion_impact: Effect of increased trust on conversion/retention (0-1)
        """
        self.inputs.brand_value = brand_value
        self.inputs.ethics_premium_factor = ethics_premium_factor
        self.inputs.customers = customers
        self.inputs.revenue_per_customer = revenue_per_customer
        self.inputs.trust_factor = trust_factor
        self.inputs.conversion_impact = conversion_impact
    
    def _calculate_brand_value_benefits(self) -> float:
        """
        Calculate the NPV of brand value benefits.
        
        Returns:
            NPV of brand value benefits
        """
        # Apply industry-specific brand multiplier
        brand_multiplier = self.industry_multipliers["brand"]
        
        # Brand equity enhancement benefit
        brand_equity_benefit = self.inputs.brand_value * self.inputs.ethics_premium_factor * brand_multiplier
        
        # Customer trust improvement benefit
        customer_trust_benefit = self.inputs.customers * self.inputs.revenue_per_customer * \
                               self.inputs.trust_factor * self.inputs.conversion_impact * brand_multiplier
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        
        # Brand equity benefit is spread over the time horizon
        yearly_brand_equity = brand_equity_benefit / self.inputs.time_horizon
        
        for _ in range(1, self.inputs.time_horizon + 1):
            yearly_benefits.append(yearly_brand_equity + customer_trust_benefit)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Regulatory Compliance Benefit Methods ------
    
    def set_regulatory_compliance_inputs(self, annual_compliance_costs: float, efficiency_factor: float = 0.3,
                                     penalty_probability: float = 0, average_penalty_cost: float = 0,
                                     compliance_risk_reduction: float = 0.6) -> None:
        """
        Set inputs for regulatory compliance benefits calculation.
        
        Args:
            annual_compliance_costs: Current spending on AI compliance in currency units
            efficiency_factor: Reduction in compliance effort (0-1)
            penalty_probability: Probability of regulatory penalties (0-1)
            average_penalty_cost: Average cost of penalties in currency units
            compliance_risk_reduction: Estimated reduction in penalty risk (0-1)
        """
        self.inputs.annual_compliance_costs = annual_compliance_costs
        self.inputs.efficiency_factor = efficiency_factor
        self.inputs.penalty_probability = penalty_probability
        self.inputs.average_penalty_cost = average_penalty_cost
        self.inputs.compliance_risk_reduction = compliance_risk_reduction
    
    def _calculate_regulatory_compliance_benefits(self) -> float:
        """
        Calculate the NPV of regulatory compliance benefits.
        
        Returns:
            NPV of regulatory compliance benefits
        """
        # Apply industry-specific compliance multiplier
        compliance_multiplier = self.industry_multipliers["compliance"]
        
        # Compliance cost reduction benefit
        compliance_cost_benefit = self.inputs.annual_compliance_costs * \
                                self.inputs.efficiency_factor * compliance_multiplier
        
        # Regulatory penalty avoidance benefit
        penalty_avoidance = self.inputs.penalty_probability * self.inputs.average_penalty_cost * \
                           self.inputs.compliance_risk_reduction * compliance_multiplier
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        for _ in range(1, self.inputs.time_horizon + 1):
            yearly_benefits.append(compliance_cost_benefit + penalty_avoidance)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Innovation Enablement Benefit Methods ------
    
    def set_innovation_enablement_inputs(self, innovation_value: float, acceleration_factor: float = 0.15,
                                     ethical_market_opportunity: float = 0, ethical_barrier_factor: float = 0.5,
                                     expected_market_share: float = 0) -> None:
        """
        Set inputs for innovation enablement benefits calculation.
        
        Args:
            innovation_value: Economic value of AI innovations in currency units
            acceleration_factor: Increase in innovation pace due to ethical clarity (0-1)
            ethical_market_opportunity: Size of markets with ethical entry barriers
            ethical_barrier_factor: Degree to which ethics is a barrier to entry (0-1)
            expected_market_share: Projected market share if barrier is overcome (0-1)
        """
        self.inputs.innovation_value = innovation_value
        self.inputs.acceleration_factor = acceleration_factor
        self.inputs.ethical_market_opportunity = ethical_market_opportunity
        self.inputs.ethical_barrier_factor = ethical_barrier_factor
        self.inputs.expected_market_share = expected_market_share
    
    def _calculate_innovation_enablement_benefits(self) -> float:
        """
        Calculate the NPV of innovation enablement benefits.
        
        Returns:
            NPV of innovation enablement benefits
        """
        # Ethical innovation acceleration benefit
        innovation_benefit = self.inputs.innovation_value * self.inputs.acceleration_factor
        
        # New market access benefit
        market_access_benefit = self.inputs.ethical_market_opportunity * \
                              self.inputs.ethical_barrier_factor * \
                              self.inputs.expected_market_share
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        
        # Innovation benefits increase over time
        for year in range(1, self.inputs.time_horizon + 1):
            # Innovation benefits grow over time (linear growth model)
            year_factor = min(1.0, 0.5 + (year - 1) * 0.25)  # 50% in year 1, growing to 100% by year 3
            yearly_benefits.append((innovation_benefit + market_access_benefit) * year_factor)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Sensitivity Analysis Methods ------
    
    def _run_sensitivity_analysis(self) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for sensitivity analysis.
        
        Returns:
            Dictionary with sensitivity analysis results
        """
        # Number of simulation runs
        num_runs = 1000
        roi_results = []
        
        for _ in range(num_runs):
            # Create random variations of inputs based on DEFAULT_VARIANCE
            risk_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["risk_mitigation"],
                1 + DEFAULT_VARIANCE["risk_mitigation"]
            )
            
            operational_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["operational_efficiency"],
                1 + DEFAULT_VARIANCE["operational_efficiency"]
            )
            
            brand_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["brand_value"],
                1 + DEFAULT_VARIANCE["brand_value"]
            )
            
            compliance_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["regulatory_compliance"],
                1 + DEFAULT_VARIANCE["regulatory_compliance"]
            )
            
            innovation_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["innovation_enablement"],
                1 + DEFAULT_VARIANCE["innovation_enablement"]
            )
            
            cost_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["costs"],
                1 + DEFAULT_VARIANCE["costs"]
            )
            
            # Calculate simulated NPV for each benefit dimension
            risk_benefits = self.results.risk_mitigation_benefits * risk_factor
            operational_benefits = self.results.operational_efficiency_benefits * operational_factor
            brand_benefits = self.results.brand_value_benefits * brand_factor
            compliance_benefits = self.results.regulatory_compliance_benefits * compliance_factor
            innovation_benefits = self.results.innovation_enablement_benefits * innovation_factor
            
            # Calculate simulated total benefits and costs
            sim_benefits = risk_benefits + operational_benefits + brand_benefits + \
                          compliance_benefits + innovation_benefits
            sim_costs = self.results.npv_costs * cost_factor
            
            # Calculate simulated ROI
            if sim_costs > 0:
                sim_roi = (sim_benefits - sim_costs) / sim_costs * 100
                roi_results.append(sim_roi)
        
        # Sort results for percentile calculations
        roi_results.sort()
        
        # Get best case (95th percentile), worst case (5th percentile), and expected case (median)
        best_case_roi = np.percentile(roi_results, 95)
        worst_case_roi = np.percentile(roi_results, 5)
        confidence_interval = (worst_case_roi, best_case_roi)
        
        return {
            "best_case_roi": best_case_roi,
            "worst_case_roi": worst_case_roi,
            "confidence_interval": confidence_interval,
            "simulation_runs": num_runs
        }
    
    # ------ Main ROI Calculation Method ------
    
    def calculate_roi(self) -> ROIResults:
        """
        Calculate the overall ROI based on all inputs.
        
        Returns:
            ROIResults object with complete calculation results
        """
        # Calculate benefits for each dimension
        self.results.risk_mitigation_benefits = self._calculate_risk_mitigation_benefits()
        self.results.operational_efficiency_benefits = self._calculate_operational_efficiency_benefits()
        self.results.brand_value_benefits = self._calculate_brand_value_benefits()
        self.results.regulatory_compliance_benefits = self._calculate_regulatory_compliance_benefits()
        self.results.innovation_enablement_benefits = self._calculate_innovation_enablement_benefits()
        
        # Calculate total benefits
        self.results.npv_benefits = (
            self.results.risk_mitigation_benefits +
            self.results.operational_efficiency_benefits +
            self.results.brand_value_benefits +
            self.results.regulatory_compliance_benefits +
            self.results.innovation_enablement_benefits
        )
        
        # Calculate costs
        costs = self._calculate_total_costs()
        self.results.npv_costs = self._calculate_npv(costs)
        
        # Calculate net benefits
        self.results.net_benefits = self.results.npv_benefits - self.results.npv_costs
        
        # Calculate ROI percentage
        if self.results.npv_costs > 0:
            self.results.roi_percentage = (self.results.net_benefits / self.results.npv_costs) * 100
        else:
            self.results.roi_percentage = float('inf')  # Avoid division by zero
        
        # Calculate yearly cash flows
        yearly_benefits = [0]  # No benefits in year 0
        for year in range(1, self.inputs.time_horizon + 1):
            # Benefits are distributed evenly across years for simplicity
            yearly_benefit = self.results.npv_benefits / self.inputs.time_horizon
            yearly_benefits.append(yearly_benefit)
        
        self.results.yearly_benefits = yearly_benefits
        self.results.yearly_costs = costs
        
        # Calculate cumulative net benefits
        cumulative_net_benefits = []
        net_benefit = -costs[0]  # Initial investment (negative)
        cumulative_net_benefits.append(net_benefit)
        
        for year in range(1, self.inputs.time_horizon + 1):
            net_benefit += yearly_benefits[year] - costs[year]
            cumulative_net_benefits.append(net_benefit)
        
        self.results.cumulative_net_benefits = cumulative_net_benefits
        
        # Calculate payback period
        self.results.payback_period_months = self._calculate_payback_period(cumulative_net_benefits)
        
        # Run sensitivity analysis
        sensitivity_results = self._run_sensitivity_analysis()
        self.results.best_case_roi = sensitivity_results["best_case_roi"]
        self.results.worst_case_roi = sensitivity_results["worst_case_roi"]
        self.results.confidence_interval = sensitivity_results["confidence_interval"]
        
        return self.results
    
    # ------ Reporting Methods ------
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of the ROI calculation results.
        
        Returns:
            Dictionary with summary report data
        """
        if not hasattr(self.results, 'roi_percentage') or self.results.roi_percentage == 0:
            raise ValueError("ROI calculation has not been performed. Call calculate_roi() first.")
        
        return {
            "organization": {
                "name": self.inputs.organization_name,
                "industry": self.inputs.industry,
                "calculation_date": self.calculation_date.strftime("%Y-%m-%d")
            },
            "roi_summary": {
                "roi_percentage": round(self.results.roi_percentage, 2),
                "net_benefits": round(self.results.net_benefits, 2),
                "payback_period_months": round(self.results.payback_period_months, 1),
                "time_horizon_years": self.inputs.time_horizon
            },
            "costs": {
                "implementation_cost": round(self.inputs.implementation_cost, 2),
                "annual_cost": round(self.inputs.annual_cost, 2),
                "npv_total_costs": round(self.results.npv_costs, 2)
            },
            "benefits": {
                "npv_total_benefits": round(self.results.npv_benefits, 2),
                "risk_mitigation": round(self.results.risk_mitigation_benefits, 2),
                "operational_efficiency": round(self.results.operational_efficiency_benefits, 2),
                "brand_value": round(self.results.brand_value_benefits, 2),
                "regulatory_compliance": round(self.results.regulatory_compliance_benefits, 2),
                "innovation_enablement": round(self.results.innovation_enablement_benefits, 2)
            },
            "sensitivity_analysis": (lambda res=self.results: {
                "best_case_roi": round(res.best_case_roi, 2) if hasattr(res, 'best_case_roi') and res.best_case_roi is not None and not (isinstance(res.best_case_roi, float) and math.isnan(res.best_case_roi)) else "N/A",
                "worst_case_roi": round(res.worst_case_roi, 2) if hasattr(res, 'worst_case_roi') and res.worst_case_roi is not None and not (isinstance(res.worst_case_roi, float) and math.isnan(res.worst_case_roi)) else "N/A",
                "confidence_interval": (
                    round(res.confidence_interval[0], 2) if hasattr(res, 'confidence_interval') and isinstance(res.confidence_interval, tuple) and len(res.confidence_interval) == 2 and res.confidence_interval[0] is not None and not (isinstance(res.confidence_interval[0], float) and math.isnan(res.confidence_interval[0])) else "N/A",
                    round(res.confidence_interval[1], 2) if hasattr(res, 'confidence_interval') and isinstance(res.confidence_interval, tuple) and len(res.confidence_interval) == 2 and res.confidence_interval[1] is not None and not (isinstance(res.confidence_interval[1], float) and math.isnan(res.confidence_interval[1])) else "N/A"
                )
            })()
        }
    
    def export_to_json(self, filename: str) -> None:
        """
        Export the ROI calculation results to a JSON file.
        
        Args:
            filename: Path to the output JSON file
        """
        summary = self.generate_summary_report()
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=4)
    
    def generate_detailed_report(self) -> str:
        """
        Generate a detailed text report of the ROI calculation results.
        
        Returns:
            Formatted string with detailed report
        """
        if not hasattr(self.results, 'roi_percentage') or self.results.roi_percentage == 0:
            raise ValueError("ROI calculation has not been performed. Call calculate_roi() first.")
        
        report = [
            f"ATRiAN Ethics ROI Analysis for {self.inputs.organization_name}",
            f"Industry: {self.inputs.industry}",
            f"Date: {self.calculation_date.strftime('%Y-%m-%d')}\n",
            
            "ROI SUMMARY",
            "===========",
            f"ROI: {self.results.roi_percentage:.2f}%",
            f"Net Benefits (NPV): {self.results.net_benefits:,.2f}",
            f"Payback Period: {self.results.payback_period_months:.1f} months",
            f"Time Horizon: {self.inputs.time_horizon} years\n",
            
            "COSTS",
            "=====",
            f"Implementation Cost: {self.inputs.implementation_cost:,.2f}",
            f"Annual Cost: {self.inputs.annual_cost:,.2f}",
            f"Total Costs (NPV): {self.results.npv_costs:,.2f}\n",
            
            "BENEFITS BY CATEGORY",
            "====================",
            f"Total Benefits (NPV): {self.results.npv_benefits:,.2f}",
            f"  Risk Mitigation: {self.results.risk_mitigation_benefits:,.2f} " + 
            f"({self.results.risk_mitigation_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Operational Efficiency: {self.results.operational_efficiency_benefits:,.2f} " + 
            f"({self.results.operational_efficiency_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Brand Value: {self.results.brand_value_benefits:,.2f} " + 
            f"({self.results.brand_value_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Regulatory Compliance: {self.results.regulatory_compliance_benefits:,.2f} " + 
            f"({self.results.regulatory_compliance_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Innovation Enablement: {self.results.innovation_enablement_benefits:,.2f} " + 
            f"({self.results.innovation_enablement_benefits/self.results.npv_benefits*100:.1f}%)\n",
            
            "SENSITIVITY ANALYSIS",
            "====================",
            f"Best Case ROI (95th percentile): {self.results.best_case_roi:.2f}%",
            f"Expected ROI: {self.results.roi_percentage:.2f}%",
            f"Worst Case ROI (5th percentile): {self.results.worst_case_roi:.2f}%",
            f"90% Confidence Interval: ({self.results.confidence_interval[0]:.2f}%, {self.results.confidence_interval[1]:.2f}%)\n",
            
            "YEARLY BREAKDOWN",
            "================",
        ]
        
        # Add yearly breakdown table
        report.append("Year | Benefits | Costs | Net Benefits | Cumulative Net Benefits")
        report.append("-" * 75)
        
        for year in range(self.inputs.time_horizon + 1):
            report.append(
                f"{year} | {self.results.yearly_benefits[year]:,.2f} | {self.results.yearly_costs[year]:,.2f} | " +
                f"{self.results.yearly_benefits[year] - self.results.yearly_costs[year]:,.2f} | " +
                f"{self.results.cumulative_net_benefits[year]:,.2f}"
            )
        
        return "\n".join(report)
    
    # ------ Operational Efficiency Benefit Methods ------
    
    def set_operational_efficiency_inputs(self, reviews_per_year: int, hours_per_review: float,
                                      hourly_rate: float, efficiency_gain: float = 0.5,
                                      projects_per_year: int = 0, average_delay_cost: float = 0,
                                      delay_reduction_factor: float = 0.3) -> None:
        """
        Set inputs for operational efficiency benefits calculation.
        
        Args:
            reviews_per_year: Number of ethical reviews conducted annually
            hours_per_review: Average time spent per review in hours
            hourly_rate: Fully loaded cost of reviewer time in currency units
            efficiency_gain: Percentage reduction in review time (0-1)
            projects_per_year: Number of AI projects implemented annually
            average_delay_cost: Cost of project delays due to ethical reviews
            delay_reduction_factor: Expected reduction in delays (0-1)
        """
        self.inputs.reviews_per_year = reviews_per_year
        self.inputs.hours_per_review = hours_per_review
        self.inputs.efficiency_gain = efficiency_gain
        self.inputs.hourly_rate = hourly_rate
        self.inputs.projects_per_year = projects_per_year
        self.inputs.average_delay_cost = average_delay_cost
        self.inputs.delay_reduction_factor = delay_reduction_factor
    
    def _calculate_operational_efficiency_benefits(self) -> float:
        """
        Calculate the NPV of operational efficiency benefits.
        
        Returns:
            NPV of operational efficiency benefits
        """
        # Review time reduction benefit
        review_time_benefit = self.inputs.reviews_per_year * self.inputs.hours_per_review * \
                            self.inputs.efficiency_gain * self.inputs.hourly_rate
        
        # Development acceleration benefit
        development_benefit = self.inputs.projects_per_year * self.inputs.average_delay_cost * \
                            self.inputs.delay_reduction_factor
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        for _ in range(1, self.inputs.time_horizon + 1):
            yearly_benefits.append(review_time_benefit + development_benefit)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Brand Value Benefit Methods ------
    
    def set_brand_value_inputs(self, brand_value: float, ethics_premium_factor: float = 0.01,
                          customers: int = 0, revenue_per_customer: float = 0,
                          trust_factor: float = 0.5, conversion_impact: float = 0.02) -> None:
        """
        Set inputs for brand value benefits calculation.
        
        Args:
            brand_value: Estimated total brand value in currency units
            ethics_premium_factor: Incremental value from ethical AI positioning (0-1)
            customers: Number of customers/users
            revenue_per_customer: Annual revenue per customer in currency units
            trust_factor: Impact of ethical practices on trust (0-1)
            conversion_impact: Effect of increased trust on conversion/retention (0-1)
        """
        self.inputs.brand_value = brand_value
        self.inputs.ethics_premium_factor = ethics_premium_factor
        self.inputs.customers = customers
        self.inputs.revenue_per_customer = revenue_per_customer
        self.inputs.trust_factor = trust_factor
        self.inputs.conversion_impact = conversion_impact
    
    def _calculate_brand_value_benefits(self) -> float:
        """
        Calculate the NPV of brand value benefits.
        
        Returns:
            NPV of brand value benefits
        """
        # Apply industry-specific brand multiplier
        brand_multiplier = self.industry_multipliers["brand"]
        
        # Brand equity enhancement benefit
        brand_equity_benefit = self.inputs.brand_value * self.inputs.ethics_premium_factor * brand_multiplier
        
        # Customer trust improvement benefit
        customer_trust_benefit = self.inputs.customers * self.inputs.revenue_per_customer * \
                               self.inputs.trust_factor * self.inputs.conversion_impact * brand_multiplier
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        
        # Brand equity benefit is spread over the time horizon
        yearly_brand_equity = brand_equity_benefit / self.inputs.time_horizon
        
        for _ in range(1, self.inputs.time_horizon + 1):
            yearly_benefits.append(yearly_brand_equity + customer_trust_benefit)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Regulatory Compliance Benefit Methods ------
    
    def set_regulatory_compliance_inputs(self, annual_compliance_costs: float, efficiency_factor: float = 0.3,
                                     penalty_probability: float = 0, average_penalty_cost: float = 0,
                                     compliance_risk_reduction: float = 0.6) -> None:
        """
        Set inputs for regulatory compliance benefits calculation.
        
        Args:
            annual_compliance_costs: Current spending on AI compliance in currency units
            efficiency_factor: Reduction in compliance effort (0-1)
            penalty_probability: Probability of regulatory penalties (0-1)
            average_penalty_cost: Average cost of penalties in currency units
            compliance_risk_reduction: Estimated reduction in penalty risk (0-1)
        """
        self.inputs.annual_compliance_costs = annual_compliance_costs
        self.inputs.efficiency_factor = efficiency_factor
        self.inputs.penalty_probability = penalty_probability
        self.inputs.average_penalty_cost = average_penalty_cost
        self.inputs.compliance_risk_reduction = compliance_risk_reduction
    
    def _calculate_regulatory_compliance_benefits(self) -> float:
        """
        Calculate the NPV of regulatory compliance benefits.
        
        Returns:
            NPV of regulatory compliance benefits
        """
        # Apply industry-specific compliance multiplier
        compliance_multiplier = self.industry_multipliers["compliance"]
        
        # Compliance cost reduction benefit
        compliance_cost_benefit = self.inputs.annual_compliance_costs * \
                                self.inputs.efficiency_factor * compliance_multiplier
        
        # Regulatory penalty avoidance benefit
        penalty_avoidance = self.inputs.penalty_probability * self.inputs.average_penalty_cost * \
                           self.inputs.compliance_risk_reduction * compliance_multiplier
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        for _ in range(1, self.inputs.time_horizon + 1):
            yearly_benefits.append(compliance_cost_benefit + penalty_avoidance)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Innovation Enablement Benefit Methods ------
    
    def set_innovation_enablement_inputs(self, innovation_value: float, acceleration_factor: float = 0.15,
                                     ethical_market_opportunity: float = 0, ethical_barrier_factor: float = 0.5,
                                     expected_market_share: float = 0) -> None:
        """
        Set inputs for innovation enablement benefits calculation.
        
        Args:
            innovation_value: Economic value of AI innovations in currency units
            acceleration_factor: Increase in innovation pace due to ethical clarity (0-1)
            ethical_market_opportunity: Size of markets with ethical entry barriers
            ethical_barrier_factor: Degree to which ethics is a barrier to entry (0-1)
            expected_market_share: Projected market share if barrier is overcome (0-1)
        """
        self.inputs.innovation_value = innovation_value
        self.inputs.acceleration_factor = acceleration_factor
        self.inputs.ethical_market_opportunity = ethical_market_opportunity
        self.inputs.ethical_barrier_factor = ethical_barrier_factor
        self.inputs.expected_market_share = expected_market_share
    
    def _calculate_innovation_enablement_benefits(self) -> float:
        """
        Calculate the NPV of innovation enablement benefits.
        
        Returns:
            NPV of innovation enablement benefits
        """
        # Ethical innovation acceleration benefit
        innovation_benefit = self.inputs.innovation_value * self.inputs.acceleration_factor
        
        # New market access benefit
        market_access_benefit = self.inputs.ethical_market_opportunity * \
                              self.inputs.ethical_barrier_factor * \
                              self.inputs.expected_market_share
        
        # Calculate yearly benefits (starting at year 1, not year 0)
        yearly_benefits = [0]  # No benefits in year 0
        
        # Innovation benefits increase over time
        for year in range(1, self.inputs.time_horizon + 1):
            # Innovation benefits grow over time (linear growth model)
            year_factor = min(1.0, 0.5 + (year - 1) * 0.25)  # 50% in year 1, growing to 100% by year 3
            yearly_benefits.append((innovation_benefit + market_access_benefit) * year_factor)
        
        # Return NPV of benefits
        return self._calculate_npv(yearly_benefits)
    
    # ------ Sensitivity Analysis Methods ------
    
    def _run_sensitivity_analysis(self) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for sensitivity analysis.
        
        Returns:
            Dictionary with sensitivity analysis results
        """
        # Number of simulation runs
        num_runs = 1000
        roi_results = []
        
        for _ in range(num_runs):
            # Create random variations of inputs based on DEFAULT_VARIANCE
            risk_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["risk_mitigation"],
                1 + DEFAULT_VARIANCE["risk_mitigation"]
            )
            
            operational_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["operational_efficiency"],
                1 + DEFAULT_VARIANCE["operational_efficiency"]
            )
            
            brand_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["brand_value"],
                1 + DEFAULT_VARIANCE["brand_value"]
            )
            
            compliance_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["regulatory_compliance"],
                1 + DEFAULT_VARIANCE["regulatory_compliance"]
            )
            
            innovation_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["innovation_enablement"],
                1 + DEFAULT_VARIANCE["innovation_enablement"]
            )
            
            cost_factor = np.random.uniform(
                1 - DEFAULT_VARIANCE["costs"],
                1 + DEFAULT_VARIANCE["costs"]
            )
            
            # Calculate simulated NPV for each benefit dimension
            risk_benefits = self.results.risk_mitigation_benefits * risk_factor
            operational_benefits = self.results.operational_efficiency_benefits * operational_factor
            brand_benefits = self.results.brand_value_benefits * brand_factor
            compliance_benefits = self.results.regulatory_compliance_benefits * compliance_factor
            innovation_benefits = self.results.innovation_enablement_benefits * innovation_factor
            
            # Calculate simulated total benefits and costs
            sim_benefits = risk_benefits + operational_benefits + brand_benefits + \
                          compliance_benefits + innovation_benefits
            sim_costs = self.results.npv_costs * cost_factor
            
            # Calculate simulated ROI
            if sim_costs > 0:
                sim_roi = (sim_benefits - sim_costs) / sim_costs * 100
                roi_results.append(sim_roi)
        
        # Sort results for percentile calculations
        roi_results.sort()
        
        # Get best case (95th percentile), worst case (5th percentile), and expected case (median)
        best_case_roi = np.percentile(roi_results, 95)
        worst_case_roi = np.percentile(roi_results, 5)
        confidence_interval = (worst_case_roi, best_case_roi)
        
        return {
            "best_case_roi": best_case_roi,
            "worst_case_roi": worst_case_roi,
            "confidence_interval": confidence_interval,
            "simulation_runs": num_runs
        }
    
    # ------ Main ROI Calculation Method ------
    
    def calculate_roi(self) -> ROIResults:
        """
        Calculate the overall ROI based on all inputs.
        
        Returns:
            ROIResults object with complete calculation results
        """
        # Calculate benefits for each dimension
        self.results.risk_mitigation_benefits = self._calculate_risk_mitigation_benefits()
        self.results.operational_efficiency_benefits = self._calculate_operational_efficiency_benefits()
        self.results.brand_value_benefits = self._calculate_brand_value_benefits()
        self.results.regulatory_compliance_benefits = self._calculate_regulatory_compliance_benefits()
        self.results.innovation_enablement_benefits = self._calculate_innovation_enablement_benefits()
        
        # Calculate total benefits
        self.results.npv_benefits = (
            self.results.risk_mitigation_benefits +
            self.results.operational_efficiency_benefits +
            self.results.brand_value_benefits +
            self.results.regulatory_compliance_benefits +
            self.results.innovation_enablement_benefits
        )
        
        # Calculate costs
        costs = self._calculate_total_costs()
        self.results.npv_costs = self._calculate_npv(costs)
        
        # Calculate net benefits
        self.results.net_benefits = self.results.npv_benefits - self.results.npv_costs
        
        # Calculate ROI percentage
        if self.results.npv_costs > 0:
            self.results.roi_percentage = (self.results.net_benefits / self.results.npv_costs) * 100
        else:
            self.results.roi_percentage = float('inf')  # Avoid division by zero
        
        # Calculate yearly cash flows
        yearly_benefits = [0]  # No benefits in year 0
        for year in range(1, self.inputs.time_horizon + 1):
            # Benefits are distributed evenly across years for simplicity
            yearly_benefit = self.results.npv_benefits / self.inputs.time_horizon
            yearly_benefits.append(yearly_benefit)
        
        self.results.yearly_benefits = yearly_benefits
        self.results.yearly_costs = costs
        
        # Calculate cumulative net benefits
        cumulative_net_benefits = []
        net_benefit = -costs[0]  # Initial investment (negative)
        cumulative_net_benefits.append(net_benefit)
        
        for year in range(1, self.inputs.time_horizon + 1):
            net_benefit += yearly_benefits[year] - costs[year]
            cumulative_net_benefits.append(net_benefit)
        
        self.results.cumulative_net_benefits = cumulative_net_benefits
        
        # Calculate payback period
        self.results.payback_period_months = self._calculate_payback_period(cumulative_net_benefits)
        
        # Run sensitivity analysis
        sensitivity_results = self._run_sensitivity_analysis()
        self.results.best_case_roi = sensitivity_results["best_case_roi"]
        self.results.worst_case_roi = sensitivity_results["worst_case_roi"]
        self.results.confidence_interval = sensitivity_results["confidence_interval"]
        
        return self.results
    
    # ------ Reporting Methods ------
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of the ROI calculation results.
        
        Returns:
            Dictionary with summary report data
        """
        if not hasattr(self.results, 'roi_percentage') or self.results.roi_percentage == 0:
            raise ValueError("ROI calculation has not been performed. Call calculate_roi() first.")
        
        return {
            "organization": {
                "name": self.inputs.organization_name,
                "industry": self.inputs.industry,
                "calculation_date": self.calculation_date.strftime("%Y-%m-%d")
            },
            "roi_summary": {
                "roi_percentage": round(self.results.roi_percentage, 2),
                "net_benefits": round(self.results.net_benefits, 2),
                "payback_period_months": round(self.results.payback_period_months, 1),
                "time_horizon_years": self.inputs.time_horizon
            },
            "costs": {
                "implementation_cost": round(self.inputs.implementation_cost, 2),
                "annual_cost": round(self.inputs.annual_cost, 2),
                "npv_total_costs": round(self.results.npv_costs, 2)
            },
            "benefits": {
                "npv_total_benefits": round(self.results.npv_benefits, 2),
                "risk_mitigation": round(self.results.risk_mitigation_benefits, 2),
                "operational_efficiency": round(self.results.operational_efficiency_benefits, 2),
                "brand_value": round(self.results.brand_value_benefits, 2),
                "regulatory_compliance": round(self.results.regulatory_compliance_benefits, 2),
                "innovation_enablement": round(self.results.innovation_enablement_benefits, 2)
            },
            "sensitivity_analysis": {
                "best_case_roi": round(self.results.best_case_roi, 2),
                "worst_case_roi": round(self.results.worst_case_roi, 2),
                "confidence_interval": (
                    round(self.results.confidence_interval[0], 2),
                    round(self.results.confidence_interval[1], 2)
                )
            }
        }
    
    def export_to_json(self, filename: str) -> None:
        """
        Export the ROI calculation results to a JSON file.
        
        Args:
            filename: Path to the output JSON file
        """
        summary = self.generate_summary_report()
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=4)
    
    def generate_detailed_report(self) -> str:
        """
        Generate a detailed text report of the ROI calculation results.
        
        Returns:
            Formatted string with detailed report
        """
        if not hasattr(self.results, 'roi_percentage') or self.results.roi_percentage == 0:
            raise ValueError("ROI calculation has not been performed. Call calculate_roi() first.")
        
        report = [
            f"ATRiAN Ethics ROI Analysis for {self.inputs.organization_name}",
            f"Industry: {self.inputs.industry}",
            f"Date: {self.calculation_date.strftime('%Y-%m-%d')}\n",
            
            "ROI SUMMARY",
            "===========",
            f"ROI: {self.results.roi_percentage:.2f}%",
            f"Net Benefits (NPV): {self.results.net_benefits:,.2f}",
            f"Payback Period: {self.results.payback_period_months:.1f} months",
            f"Time Horizon: {self.inputs.time_horizon} years\n",
            
            "COSTS",
            "=====",
            f"Implementation Cost: {self.inputs.implementation_cost:,.2f}",
            f"Annual Cost: {self.inputs.annual_cost:,.2f}",
            f"Total Costs (NPV): {self.results.npv_costs:,.2f}\n",
            
            "BENEFITS BY CATEGORY",
            "====================",
            f"Total Benefits (NPV): {self.results.npv_benefits:,.2f}",
            f"  Risk Mitigation: {self.results.risk_mitigation_benefits:,.2f} " + 
            f"({self.results.risk_mitigation_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Operational Efficiency: {self.results.operational_efficiency_benefits:,.2f} " + 
            f"({self.results.operational_efficiency_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Brand Value: {self.results.brand_value_benefits:,.2f} " + 
            f"({self.results.brand_value_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Regulatory Compliance: {self.results.regulatory_compliance_benefits:,.2f} " + 
            f"({self.results.regulatory_compliance_benefits/self.results.npv_benefits*100:.1f}%)",
            f"  Innovation Enablement: {self.results.innovation_enablement_benefits:,.2f} " + 
            f"({self.results.innovation_enablement_benefits/self.results.npv_benefits*100:.1f}%)\n",
            
            "SENSITIVITY ANALYSIS",
            "====================",
            f"Best Case ROI (95th percentile): {self.results.best_case_roi:.2f}%",
            f"Expected ROI: {self.results.roi_percentage:.2f}%",
            f"Worst Case ROI (5th percentile): {self.results.worst_case_roi:.2f}%",
            f"90% Confidence Interval: ({self.results.confidence_interval[0]:.2f}%, {self.results.confidence_interval[1]:.2f}%)\n",
            
            "YEARLY BREAKDOWN",
            "================",
        ]
        
        # Add yearly breakdown table
        report.append("Year | Benefits | Costs | Net Benefits | Cumulative Net Benefits")
        report.append("-" * 75)
        
        for year in range(self.inputs.time_horizon + 1):
            report.append(
                f"{year} | {self.results.yearly_benefits[year]:,.2f} | {self.results.yearly_costs[year]:,.2f} | " +
                f"{self.results.yearly_benefits[year] - self.results.yearly_costs[year]:,.2f} | " +
                f"{self.results.cumulative_net_benefits[year]:,.2f}"
            )
        
        return "\n".join(report)