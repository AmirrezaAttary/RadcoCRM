import operator
from functools import reduce
from itertools import product

from django.db import models
from rest_framework import filters

# حروف: شکل فارسی ↔ شکل عربی

_AR_TO_FA_LETTERS = {"ي": "ی", "ى": "ی", "ك": "ک"}
_FA_TO_AR_LETTERS = {"ی": "ي", "ک": "ك"}

# ارقام: لاتین، فارسی (۰-۹)، عربی (٠-٩)
_LATIN = "0123456789"
_PERSIAN = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC = "٠١٢٣٤٥٦٧٨٩"
_TO_LATIN = {ord(c): _LATIN[i] for i, c in enumerate(_PERSIAN)}
_TO_LATIN.update({ord(c): _LATIN[i] for i, c in enumerate(_ARABIC)})
_TO_LATIN.update({ord(k): v for k, v in _AR_TO_FA_LETTERS.items()})


def normalize(text: str) -> str:
    """ي/ى→ی ، ك→ک ، ارقام فارسی و عربی→لاتین"""
    return text.translate(_TO_LATIN)


def term_variants(term: str) -> list[str]:
    """
    همهٔ شکل‌هایی که یک عبارت ممکن است در دیتابیس ذخیره شده باشد:
    حروف فارسی/عربی × ارقام لاتین/فارسی/عربی.
    اگر عبارت حرف یا رقم نداشته باشد، فقط خودش برمی‌گردد.
    """
    base = normalize(term)
    has_letters = any(c in base for c in "یک")
    has_digits = any(c in base for c in _LATIN)

    letter_maps = [{}]
    if has_letters:
        letter_maps.append(_FA_TO_AR_LETTERS)

    digit_maps = [{}]
    if has_digits:
        digit_maps.append({ord(_LATIN[i]): _PERSIAN[i] for i in range(10)})
        digit_maps.append({ord(_LATIN[i]): _ARABIC[i] for i in range(10)})

    variants = []
    for lm, dm in product(letter_maps, digit_maps):
        v = base
        if lm:
            v = v.translate({ord(k): val for k, val in lm.items()})
        if dm:
            v = v.translate(dm)
        if v not in variants:
            variants.append(v)
    return variants


class PersianSearchFilter(filters.SearchFilter):
    """
    SearchFilter استاندارد DRF + سازگاری با تفاوت‌های نوشتاری فارسی:
    «علي» با «علی» ، «كتاب» با «کتاب» و «۰۹۱۲» با «0912» یکی حساب می‌شوند.
    """

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        try:
            orm_lookups = [
                self.construct_search(str(f), queryset) for f in search_fields
            ]
        except TypeError:  # نسخه‌های قدیمی DRF
            orm_lookups = [self.construct_search(str(f)) for f in search_fields]

        base = queryset
        conditions = []
        for term in search_terms:
            queries = [
                models.Q(**{lookup: variant})
                for lookup in orm_lookups
                for variant in term_variants(term)
            ]
            conditions.append(reduce(operator.or_, queries))

        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # حذف رکوردهای تکراری (جستجو روی رابطهٔ چندبه‌چند)، مثل خود DRF
            queryset = base.filter(
                models.Exists(queryset.filter(pk=models.OuterRef("pk")))
            )
        return queryset
