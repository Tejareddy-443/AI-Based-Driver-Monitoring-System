# ============================================================
# DRIVER SAFETY SCORE
# ============================================================

# Starting safety score
INITIAL_SCORE = 100


# Points deducted for each event
DROWSINESS_PENALTY = 15
YAWNING_PENALTY = 5
DISTRACTION_PENALTY = 10
PHONE_PENALTY = 15
SEATBELT_PENALTY = 10

# ============================================================
# SAFETY SCORE CLASS
# ============================================================

class SafetyScore:

    def __init__(self):

        # Start with a perfect score
        self.score = INITIAL_SCORE

        # Count detected events
        self.drowsiness_count = 0
        self.yawning_count = 0
        self.distraction_count = 0
        self.phone_count = 0
        self.seatbelt_count = 0

    # ========================================================
    # DROWSINESS
    # ========================================================

    def add_drowsiness(self):

        self.drowsiness_count += 1

        self.score -= DROWSINESS_PENALTY

        self._limit_score()


    # ========================================================
    # YAWNING
    # ========================================================

    def add_yawning(self):

        self.yawning_count += 1

        self.score -= YAWNING_PENALTY

        self._limit_score()


    # ========================================================
    # DISTRACTION
    # ========================================================

    def add_distraction(self):

        self.distraction_count += 1

        self.score -= DISTRACTION_PENALTY

        self._limit_score()

    def add_phone_usage(self):
        self.phone_count += 1
        self.score -= PHONE_PENALTY
        self._limit_score()

    def add_seatbelt_violation(self):
        self.seatbelt_count += 1

        self.score -= SEATBELT_PENALTY

        self._limit_score()


    


    # ========================================================
    # LIMIT SCORE
    # ========================================================

    def _limit_score(self):

        # Score should never go below 0
        if self.score < 0:
            self.score = 0

        # Score should never go above 100
        if self.score > 100:
            self.score = 100


    # ========================================================
    # GET SCORE
    # ========================================================

    def get_score(self):

        return self.score


    # ========================================================
    # GET SCORE STATUS
    # ========================================================

    def get_status(self):

        if self.score >= 80:
            return "SAFE"

        elif self.score >= 60:
            return "MODERATE"

        elif self.score >= 40:
            return "WARNING"

        else:
            return "HIGH RISK"