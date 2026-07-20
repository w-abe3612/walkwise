"""script/ai/budget.py — 公開契約: BudgetGuard.reserve/record/assert_available.

Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
"""

from __future__ import annotations

from dataclasses import dataclass

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class UsageEstimate:
    """token/費用の1件分。is_measured=Falseは事前見積り、Trueは実測値。"""

    tokens: int | None = None
    cost_usd: float | None = None
    is_measured: bool = False


class BudgetGuard:
    """API呼出し前に予算を判定し、実行後のusageを記録する(16節 予算制御)。"""

    def __init__(self, *, stop_usd: float, warning_usd: float | None = None) -> None:
        if stop_usd is None or stop_usd < 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "stop_usd must be a non-negative number")
        self._stop_usd = stop_usd
        self._warning_usd = warning_usd
        self._spent_usd = 0.0
        self._records: list[UsageEstimate] = []

    @property
    def spent_usd(self) -> float:
        return self._spent_usd

    @property
    def records(self) -> tuple[UsageEstimate, ...]:
        return tuple(self._records)

    def assert_available(self) -> None:
        """現在の使用済み予算がproject_stop_usdへ到達していないことを確認する。"""
        if self._spent_usd >= self._stop_usd:
            raise AppError(ErrorCode.PERMISSION_DENIED, "budget_exceeded: project_stop_usd reached")

    def reserve(self, estimate: UsageEstimate) -> None:
        """API呼出し前に、見積り費用を加算した場合の予算超過を検出する。"""
        if estimate is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "estimate is required")

        self.assert_available()

        projected = self._spent_usd + (estimate.cost_usd or 0.0)
        if projected > self._stop_usd:
            raise AppError(ErrorCode.PERMISSION_DENIED, "budget_exceeded: projected spend exceeds project_stop_usd")

    def record(self, usage: UsageEstimate) -> None:
        """API呼出し後の実測(または欠落)usageを記録する。推測値と実測値を区別して保持する。"""
        if usage is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "usage is required")

        if usage.cost_usd is not None:
            self._spent_usd += usage.cost_usd
        self._records.append(usage)
