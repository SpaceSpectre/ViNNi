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
    @staticmethod
    def calculate_loan_interest(principal: float, annual_rate: float, months: int, payment_freq: str = "monthly", compounding_freq: str = "monthly", extra_payment: float = 0.0) -> dict:
        """
        Amortization calc with support for:
        - Mismatched compounding (Effective Rate)
        - Extra Payments (Payoff Time)
        """
        P = Decimal(str(principal))
        r_annual = Decimal(str(annual_rate))
        extra = Decimal(str(extra_payment))
        
        # Frequency Map
        FREQ_MAP = {
            "daily": 365, "weekly": 52, "bi-weekly": 26, "biweekly": 26,
            "semi-monthly": 24, "monthly": 12, "quarterly": 4, 
            "semi-annually": 2, "annually": 1
        }
        
        p_freq = FREQ_MAP.get(payment_freq.lower(), 12)
        c_freq = FREQ_MAP.get(compounding_freq.lower().replace(" compounded", ""), 12) # Robust key
        
        # Calculate Number of Payments (n)
        term_years = Decimal(months) / 12
        n_scheduled = int(term_years * p_freq)
        
        # Edge Case: Immediate Repayment (0 months)
        if n_scheduled <= 0:
             return {
                "payment_frequency": payment_freq,
                "compounding_frequency": compounding_freq,
                "periodic_rate": 0.0,
                "payment_amount": float(principal),
                "num_payments": 1, # Treated as 1 lump sum
                "total_payment": float(principal),
                "total_interest": 0.0,
                "extra_payment_monthly": 0.0,
                "new_payoff_time_months": 0.0,
                "time_saved_months": 0.0,
                "interest_saved": 0.0
            }

        # Effective Rate Calc: r_period = (1 + r_nominal/c)^(c/p) - 1
        # 1. Base per compounding period
        r_base = r_annual / c_freq
        # 2. Exponent
        exponent = Decimal(c_freq) / Decimal(p_freq)
        # 3. Effective Rate per Payment Period
        r_period = ((1 + r_base) ** exponent) - 1
        
        # Monthly (or Periodic) Payment: PMT = P * (r / (1 - (1+r)^-n))
        if r_period > 0:
            pmt = P * (r_period / (1 - (1 + r_period) ** -n_scheduled))
        else:
            pmt = P / n_scheduled
            
        # Extra Payment Logic (Part d)
        actual_pmt = pmt + extra
        
        # Recalculate N with extra payment
        # n_actual = -log(1 - (r * P) / actual_pmt) / log(1 + r)
        n_actual = n_scheduled
        interest_saved = Decimal(0)
        time_saved_months = Decimal(0)
        
        if extra > 0 and actual_pmt > 0:
            try:
                # Check for negative log (if PMT < Interest) - unlikely here
                # Using float for log
                num = 1 - (float(r_period) * float(P)) / float(actual_pmt)
                if num > 0:
                    import math
                    n_new_float = -math.log(num) / math.log(1 + float(r_period))
                    n_actual = Decimal(str(n_new_float))
                    
                    # Totals
                    total_payment_new = actual_pmt * n_actual
                    total_interest_new = total_payment_new - P
                    
                    # Original Totals
                    total_payment_orig = pmt * n_scheduled
                    total_interest_orig = total_payment_orig - P
                    
                    interest_saved = total_interest_orig - total_interest_new
                    
                    # Time Saved (in months)
                    # Diff in periods / periods_per_year * 12
                    periods_saved = Decimal(n_scheduled) - n_actual
                    time_saved_months = periods_saved / Decimal(p_freq) * 12
            except:
                pass # Fallback to standard
                
        total_payment = pmt * n_scheduled
        total_interest = total_payment - P
        
        return {
            "payment_frequency": payment_freq,
            "compounding_frequency": compounding_freq,
            "periodic_rate": float(round(r_period, 8)),
            "payment_amount": float(round(pmt, 2)),
            "num_payments": int(n_scheduled),
            "total_payment": float(round(total_payment, 2)),
            "total_interest": float(round(total_interest, 2)),
            # Extra Payment Data
            "extra_payment_monthly": float(round(extra, 2)),
            "new_payoff_time_months": float(round(term_years * 12 - time_saved_months, 1)),
            "time_saved_months": float(round(time_saved_months, 1)),
            "interest_saved": float(round(interest_saved, 2))
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
