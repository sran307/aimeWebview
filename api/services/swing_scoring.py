# yourapp/services/swing_scoring.py
from datetime import datetime
from django.db.models import (
    Max, Avg, Count, Q, F, Subquery, OuterRef, Value
)
from django.db import transaction
from django.utils import timezone

from api.models import*


def safe_float(v):
    try:
        return 0.0 if v is None else float(v)
    except Exception:
        return 0.0


def compute_ranks_for_date(target_date=None):
    """
    Compute all ranks for SwingStocks entries on target_date (defaults to most recent).
    Returns number of updated rows.
    """
    # 1) pick date
    if target_date is None:
        target_date = SwingStocks.objects.aggregate(Max('date'))['date__max']
        if target_date is None:
            return 0

    # 2) Trendy sectors set (for quick lookup)
    trending_sectors = set(
        TrendySector.objects.values_list('sector', flat=True)
    )

    # 3) Prepare Subqueries for latest holdings for each stock
    latest_holdings_qs = StockHoldings.objects.filter(stock=OuterRef('stock')).order_by('-date')

    # Subqueries for holdings fields (first row of latest holdings)
    uPlPctT_sub = Subquery(latest_holdings_qs.values('uPlPctT')[:1])
    mfPctT_sub = Subquery(latest_holdings_qs.values('mfPctT')[:1])
    isPctT_sub = Subquery(latest_holdings_qs.values('isPctT')[:1])
    fiPctT_sub = Subquery(latest_holdings_qs.values('fiPctT')[:1])

    # 4) Annotate the SwingStocks queryset to fetch related metrics in bulk
    ss_qs = SwingStocks.objects.filter(date=target_date).annotate(
        # commentary counts (positive / negative)
        pos_comments=Count('stock__cmnt_stock_name', filter=Q(stock__cmnt_stock_name__mood='Positive')),
        neg_comments=Count('stock__cmnt_stock_name', filter=Q(stock__cmnt_stock_name__mood='Negative')),

        # Dividend yield (take max/avg from StockRatios)
        div_yield=Max('stock__ratio_stock_name__divYield'),

        # Forecasts (use avg of available forecasts)
        forecast_buy=Avg('stock__forecast_stock_name__buy'),
        forecast_sell=Avg('stock__forecast_stock_name__sell'),

        # Leverage - debtEq
        debt_eq=Max('stock__lvr_stock_name__debtEq'),

        # Latest holdings fields via subquery
        holding_uPlPctT=uPlPctT_sub,
        holding_mfPctT=mfPctT_sub,
        holding_isPctT=isPctT_sub,
        holding_fiPctT=fiPctT_sub,
    )

    # We'll create instances and bulk_update them
    to_update = []

    # Loop through annotated queryset (no extra DB queries for annotated fields)
    for ss in ss_qs.select_related('stock'):
        # initialize base rank
        rank = 1.0

        # --- commentary rank ---
        pos = safe_float(ss.pos_comments)
        neg = safe_float(ss.neg_comments)
        # original logic: +10 per positive, -10 per negative
        com_rank = 1 + (pos * 10) - (neg * 10)
        rank = com_rank

        # --- dividend rank ---
        div_y = safe_float(ss.div_yield)
        if div_y > 0:
            # original logic: multiplier = 1 + divYield
            ratio_rank = 1 + div_y
            rank = rank * ratio_rank
            div_rank = div_y
        else:
            div_rank = 0.0

        # --- holdings rank ---
        uPl = safe_float(ss.holding_uPlPctT)
        mf = safe_float(ss.holding_mfPctT)
        isp = safe_float(ss.holding_isPctT)
        fi = safe_float(ss.holding_fiPctT)

        hol_rank = uPl + mf + isp + fi
        rank = rank + hol_rank

        # --- forecast rank ---
        buy = safe_float(ss.forecast_buy)
        sell = safe_float(ss.forecast_sell)
        fore_rank = buy - sell
        rank = rank + fore_rank

        # --- leverage adjustment (debtEq) ---
        debt_eq = safe_float(ss.debt_eq)
        if debt_eq and debt_eq > 0:
            # avoid divide-by-zero; original code divided by debtEq
            try:
                rank = rank / debt_eq
            except Exception:
                pass  # leave rank as-is if weird values
        else:
            # if no debt data, keep rank as-is or apply light penalty
            pass

        # Prepare final fields
        tot_rank = float(rank)
        is_sector_flag = False
        # sector boost if this stock's sector is trending
        stock_sector = ss.stock.sector if ss.stock else None
        if stock_sector and stock_sector in trending_sectors:
            tot_rank = tot_rank + 50
            is_sector_flag = True

        # Update instance fields (we will bulk_update)
        ss.com_rank = round(com_rank, 4)
        ss.div_rank = round(div_rank, 4)
        ss.hol_rank = round(hol_rank, 4)
        ss.fore_rank = round(fore_rank, 4)
        ss.tot_rank = round(tot_rank, 6)
        ss.is_sector = is_sector_flag

        to_update.append(ss)

    # Bulk update all modified SwingStocks (single DB write per batch)
    if to_update:
        # fields to update
        with transaction.atomic():
            SwingStocks.objects.bulk_update(
                to_update,
                ['com_rank', 'div_rank', 'hol_rank', 'fore_rank', 'tot_rank', 'is_sector']
            )

    return len(to_update)
