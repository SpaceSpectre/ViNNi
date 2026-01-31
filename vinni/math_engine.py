import math
from decimal import Decimal, getcontext

# Set precision high
getcontext().prec = 28

class ProbabilityEngine:
    @staticmethod
    def combinations(n: int, k: int) -> int:
        return math.comb(n, k)
    
    @staticmethod
    def permutations(n: int, k: int) -> int:
        return math.perm(n, k)
    
    @staticmethod
    def exponents(n: int, k: int) -> int:
        return n ** k

    @staticmethod
    def solve_blackjack_probability() -> dict:
        """Deterministic solution for Blackjack (2 cards)."""
        # C(52, 2)
        total = math.comb(52, 2)
        # Target: Ace (4) * Ten-Value (16)
        target = 4 * 16
        prob = Decimal(target) / Decimal(total)
        return {
            "total_hands": total,
            "target_hands": target,
            "probability": float(round(prob, 6)),
            "percentage": f"{round(prob * 100, 4)}%"
        }

class FinanceEngine:
    @staticmethod
    def calculate_loan_interest(principal: float, annual_rate: float, months: int, payment_freq: str = "monthly") -> dict:
        """
        Amortization calc. 
        annual_rate: 0.1899 for 18.99%
        """
        P = Decimal(str(principal))
        r_annual = Decimal(str(annual_rate))
        
        # Period conversions
        if payment_freq == "weekly":
            periods_per_year = 52
            n = int((months / 12) * 52)
        elif payment_freq == "daily":
             periods_per_year = 365
             n = int((months / 12) * 365)
        else:
            periods_per_year = 12
            n = months
            
        r_period = r_annual / periods_per_year
        
        # Monthly Payment: PMT = P * (r / (1 - (1+r)^-n))
        if r_period > 0:
            pmt = P * (r_period / (1 - (1 + r_period) ** -n))
        else:
            pmt = P / n
            
        total_payment = pmt * n
        total_interest = total_payment - P
        
        return {
            "monthly_payment": float(round(pmt, 2)),
            "total_payment": float(round(total_payment, 2)),
            "total_interest": float(round(total_interest, 2))
        }

    @staticmethod
    def calculate_annuity(payment: float, rate: float, years: int, type: str = "ordinary") -> dict:
        """
        FV of Annuity.
        rate: annual (0.05)
        """
        PMT = Decimal(str(payment))
        r = Decimal(str(rate)) / 12 # Monthly
        n = years * 12
        
        # FV = PMT * (((1+r)^n - 1) / r)
        fv = PMT * (((1 + r) ** n - 1) / r)
        
        if type == "due":
            fv = fv * (1 + r)
            
        return {
            "future_value": float(round(fv, 2))
        }

    @staticmethod
    def calculate_bond(face: float, coupon_rate: float, ytm: float, years: int, freq: int = 1) -> dict:
        """
        Bond Price.
        """
        F = Decimal(str(face))
        C_rate = Decimal(str(coupon_rate))
        Y_rate = Decimal(str(ytm))
        n = years * freq
        
        coupon_payment = (F * C_rate) / freq
        y_period = Y_rate / freq
        
        # Price = sum(C / (1+y)^t) + F / (1+y)^n
        price = Decimal(0)
        # Vectorize? No, loop simple.
        for t in range(1, n + 1):
             price += coupon_payment / ((1 + y_period) ** t)
        
        price += F / ((1 + y_period) ** n)
        
        return {
            "price": float(round(price, 2))
        }

    @staticmethod
    def calculate_compound_interest(principal: float, rate_annual: float, years: int, freq: int = 1) -> dict:
        """
        Compound Interest: A = P(1 + r/n)^(nt)
        freq: 1 (Annual), 12 (Monthly), 365 (Daily)
        """
        P = Decimal(str(principal))
        r = Decimal(str(rate_annual))
        n = Decimal(str(freq))
        t = Decimal(str(years))
        
        # A = P * (1 + r/n)^(n*t)
        amount = P * ((1 + (r / n)) ** (n * t))
        interest = amount - P
        
        return {
            "principal": float(round(P, 2)),
            "future_value": float(round(amount, 2)),
            "total_interest": float(round(interest, 2)),
            "formula": f"A = {P} * (1 + {rate_annual}/{freq})^({freq}*{years})"
        }
