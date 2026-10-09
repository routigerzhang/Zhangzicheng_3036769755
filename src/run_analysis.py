from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


MIN_WAGE_AFTER = 5.05
TEMP_CLOSURE_CODES = {2, 4, 5}
PERMANENT_CLOSURE_CODE = 3


def font(size: int):
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def mean_se(values: pd.Series) -> tuple[int, float, float]:
    x = pd.to_numeric(values, errors="coerce").dropna().astype(float)
    n = len(x)
    if n == 0:
        return 0, float("nan"), float("nan")
    se = float(x.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    return n, float(x.mean()), se


def combine_se(*ses: float) -> float:
    vals = [float(x) for x in ses if np.isfinite(x)]
    return float(math.sqrt(sum(x * x for x in vals))) if vals else float("nan")


def add_derived_variables(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["store_id_unique"] = out["SHEET"].astype(str)
    duplicated = out["SHEET"].duplicated(keep=False)
    if duplicated.any():
        out.loc[duplicated, "store_id_unique"] = (
            out.loc[duplicated].groupby("SHEET").cumcount().add(1).astype(str)
            .radd(out.loc[duplicated, "SHEET"].astype(str))
        )

    out["fte1"] = out["EMPFT"] + 0.5 * out["EMPPT"] + out["NMGRS"]
    out["fte2"] = out["EMPFT2"] + 0.5 * out["EMPPT2"] + out["NMGRS2"]

    # The paper treats permanent closures as zero employment. Temporary,
    # highway, and mall-fire closures remain unavailable in the main outcome.
    out.loc[out["STATUS2"].eq(PERMANENT_CLOSURE_CODE), "fte2"] = 0.0
    out.loc[out["STATUS2"].isin(TEMP_CLOSURE_CODES), "fte2"] = np.nan
    out["fte_change"] = out["fte2"] - out["fte1"]

    out["fte2_temp_as_zero"] = out["fte2"]
    out.loc[out["STATUS2"].isin(TEMP_CLOSURE_CODES), "fte2_temp_as_zero"] = 0.0
    out["fte_change_temp_as_zero"] = out["fte2_temp_as_zero"] - out["fte1"]

    out["pct_full_time1"] = 100.0 * out["EMPFT"] / out["fte1"]
    out["pct_full_time2"] = 100.0 * out["EMPFT2"] / out["fte2"]
    out["meal_price1"] = out["PSODA"] + out["PFRY"] + out["PENTREE"]
    out["meal_price2"] = out["PSODA2"] + out["PFRY2"] + out["PENTREE2"]

    out["wage_category"] = pd.cut(
        out["WAGE_ST"],
        bins=[-np.inf, 4.25, 4.99, np.inf],
        labels=["4.25", "4.26-4.99", "5.00+"],
        right=True,
    )
    out["GAP"] = np.where(
        out["STATE"].eq(1),
        np.maximum(0.0, (MIN_WAGE_AFTER - out["WAGE_ST"]) / out["WAGE_ST"]),
        0.0,
    )
    out["GAP_CO_OWNED"] = out["GAP"] * out["CO_OWNED"]
    return out


def table2(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []

    def add(section: str, variable: str, series: pd.Series, *, binary_all=False):
        values = []
        for state in [1, 0]:
            z = series.loc[df["STATE"].eq(state)]
            if binary_all:
                n, mean, se = len(z), float(100.0 * z.mean()), float(100.0 * z.std(ddof=1) / math.sqrt(len(z)))
            else:
                n, mean, se = mean_se(z)
            values.append((n, mean, se))
        nj, pa = values
        t = (nj[1] - pa[1]) / combine_se(nj[2], pa[2])
        rows.append({
            "section": section,
            "variable": variable,
            "NJ": nj[1],
            "PA": pa[1],
            "t_NJ_minus_PA": t,
            "n_NJ": nj[0],
            "n_PA": pa[0],
        })

    chain_names = {1: "Burger King", 2: "KFC", 3: "Roy Rogers", 4: "Wendy's"}
    for chain, name in chain_names.items():
        add("Store types", name, df["CHAIN"].eq(chain).astype(float), binary_all=True)
    add("Store types", "Company-owned", df["CO_OWNED"].astype(float), binary_all=True)

    specs = [
        ("Wave 1", "FTE employment", df["fte1"], False),
        ("Wave 1", "Percentage full-time employees", df["pct_full_time1"], False),
        ("Wave 1", "Starting wage", df["WAGE_ST"], False),
        ("Wave 1", "Wage = $4.25", df["WAGE_ST"].eq(4.25).astype(float), True),
        ("Wave 1", "Price of full meal", df["meal_price1"], False),
        ("Wave 1", "Hours open", df["HRSOPEN"], False),
        ("Wave 1", "Recruiting bonus", 100.0 * df["BONUS"], False),
        ("Wave 2", "FTE employment", df["fte2"], False),
        ("Wave 2", "Percentage full-time employees", df["pct_full_time2"], False),
        ("Wave 2", "Starting wage", df["WAGE_ST2"], False),
        ("Wave 2", "Wage = $4.25", df["WAGE_ST2"].eq(4.25).astype(float), True),
        ("Wave 2", "Wage = $5.05", df["WAGE_ST2"].eq(5.05).astype(float), True),
        ("Wave 2", "Price of full meal", df["meal_price2"], False),
        ("Wave 2", "Hours open", df["HRSOPEN2"], False),
        ("Wave 2", "Recruiting bonus", 100.0 * df["SPECIAL2"], False),
    ]
    for section, variable, series, binary_all in specs:
        add(section, variable, series, binary_all=binary_all)
    return pd.DataFrame(rows)


def group_frames(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "PA": df.loc[df["STATE"].eq(0)],
        "NJ": df.loc[df["STATE"].eq(1)],
        "NJ low": df.loc[df["STATE"].eq(1) & df["wage_category"].eq("4.25")],
        "NJ mid": df.loc[df["STATE"].eq(1) & df["wage_category"].eq("4.26-4.99")],
        "NJ high": df.loc[df["STATE"].eq(1) & df["wage_category"].eq("5.00+")],
    }


def table3(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    groups = group_frames(df)
    columns = ["PA", "NJ", "NJ-PA", "NJ low", "NJ mid", "NJ high", "low-high", "mid-high"]
    output: list[dict] = []

    def values_for(series_name: str, group: pd.DataFrame):
        return mean_se(group[series_name])

    def build_level_row(label: str, series_name: str):
        stats = {k: values_for(series_name, v) for k, v in groups.items()}
        estimates = {
            "PA": stats["PA"][1], "NJ": stats["NJ"][1],
            "NJ-PA": stats["NJ"][1] - stats["PA"][1],
            "NJ low": stats["NJ low"][1], "NJ mid": stats["NJ mid"][1],
            "NJ high": stats["NJ high"][1],
            "low-high": stats["NJ low"][1] - stats["NJ high"][1],
            "mid-high": stats["NJ mid"][1] - stats["NJ high"][1],
        }
        ses = {
            "PA": stats["PA"][2], "NJ": stats["NJ"][2],
            "NJ-PA": combine_se(stats["NJ"][2], stats["PA"][2]),
            "NJ low": stats["NJ low"][2], "NJ mid": stats["NJ mid"][2],
            "NJ high": stats["NJ high"][2],
            "low-high": combine_se(stats["NJ low"][2], stats["NJ high"][2]),
            "mid-high": combine_se(stats["NJ mid"][2], stats["NJ high"][2]),
        }
        output.append({"row": label, "stat": "estimate", **estimates})
        output.append({"row": label, "stat": "standard_error", **ses})

    build_level_row("1. FTE employment before", "fte1")
    build_level_row("2. FTE employment after", "fte2")

    def build_change_row(label: str, change_name: str):
        stats = {k: mean_se(v[change_name]) for k, v in groups.items()}
        estimates = {
            "PA": stats["PA"][1], "NJ": stats["NJ"][1],
            "NJ-PA": stats["NJ"][1] - stats["PA"][1],
            "NJ low": stats["NJ low"][1], "NJ mid": stats["NJ mid"][1],
            "NJ high": stats["NJ high"][1],
            "low-high": stats["NJ low"][1] - stats["NJ high"][1],
            "mid-high": stats["NJ mid"][1] - stats["NJ high"][1],
        }
        ses = {
            "PA": stats["PA"][2], "NJ": stats["NJ"][2],
            "NJ-PA": combine_se(stats["NJ"][2], stats["PA"][2]),
            "NJ low": stats["NJ low"][2], "NJ mid": stats["NJ mid"][2],
            "NJ high": stats["NJ high"][2],
            "low-high": combine_se(stats["NJ low"][2], stats["NJ high"][2]),
            "mid-high": combine_se(stats["NJ mid"][2], stats["NJ high"][2]),
        }
        output.append({"row": label, "stat": "estimate", **estimates})
        output.append({"row": label, "stat": "standard_error", **ses})

    for group in groups.values():
        group["change_balanced"] = group["fte2"] - group["fte1"]
    build_change_row("3. Change in mean FTE", "fte_change")
    build_change_row("4. Change in mean FTE, balanced sample", "change_balanced")
    build_change_row("5. Change in mean FTE, temporary closures set to zero", "fte_change_temp_as_zero")

    row3 = next(x for x in output if x["row"].startswith("3.") and x["stat"] == "estimate")
    row3_se = next(x for x in output if x["row"].startswith("3.") and x["stat"] == "standard_error")
    validation = {
        "table3_row3_did": float(row3["NJ-PA"]),
        "table3_row3_did_se": float(row3_se["NJ-PA"]),
        "table3_row3_did_t": float(row3["NJ-PA"] / row3_se["NJ-PA"]),
        "balanced_fte_n": int(df["fte_change"].notna().sum()),
    }
    return pd.DataFrame(output, columns=["row", "stat", *columns]), validation


def make_regression_sample(df: pd.DataFrame) -> pd.DataFrame:
    return make_regression_sample_for_columns(df, "fte1", "fte2", "fte_change")


def make_regression_sample_for_columns(
    df: pd.DataFrame, fte1_column: str, fte2_column: str, change_column: str
) -> pd.DataFrame:
    employment = df[fte1_column].notna() & df[fte2_column].notna()
    baseline_wage = df["WAGE_ST"].notna()
    post_wage_or_closed = df["WAGE_ST2"].notna() | df["STATUS2"].eq(PERMANENT_CLOSURE_CODE)
    sample = df.loc[employment & baseline_wage & post_wage_or_closed].copy()
    sample["analysis_change"] = sample[change_column]
    for chain, name in [(1, "BK"), (2, "KFC"), (3, "roys")]:
        sample[name] = sample["CHAIN"].eq(chain).astype(float)
    return sample


def alternative_parttime_panel(df: pd.DataFrame, parttime_weight: float) -> pd.DataFrame:
    out = df.copy()
    out["fte1_alt"] = out["EMPFT"] + parttime_weight * out["EMPPT"] + out["NMGRS"]
    out["fte2_alt"] = out["EMPFT2"] + parttime_weight * out["EMPPT2"] + out["NMGRS2"]
    out.loc[out["STATUS2"].eq(PERMANENT_CLOSURE_CODE), "fte2_alt"] = 0.0
    out.loc[out["STATUS2"].isin(TEMP_CLOSURE_CODES), "fte2_alt"] = np.nan
    out["fte_change_alt"] = out["fte2_alt"] - out["fte1_alt"]
    return out


def ols(sample: pd.DataFrame, columns: list[str], outcome: str = "fte_change"):
    X = np.column_stack([np.ones(len(sample))] + [sample[c].to_numpy(float) for c in columns])
    y = sample[outcome].to_numpy(float)
    names = ["constant", *columns]
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError(f"Singular design matrix for columns: {columns}")
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    residual = y - X @ beta
    n, k = X.shape
    sigma2 = float(residual @ residual / (n - k))
    covariance = sigma2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(covariance))
    result = pd.DataFrame({
        "term": names,
        "coefficient": beta,
        "standard_error": se,
        "t_stat": beta / se,
    })
    result["N"] = n
    result["SER"] = math.sqrt(sigma2)
    result["R_squared"] = 1.0 - float(residual @ residual) / float(((y - y.mean()) ** 2).sum())
    return result, covariance, X, y


def table4_and_extension(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    sample = make_regression_sample(df)
    models = [
        ("(i) NJ dummy", ["STATE"]),
        ("(ii) NJ dummy + chain/ownership", ["BK", "KFC", "roys", "CO_OWNED", "STATE"]),
        ("(iii) GAP", ["GAP"]),
        ("(iv) GAP + chain/ownership", ["BK", "KFC", "roys", "CO_OWNED", "GAP"]),
        ("(v) GAP + chain/ownership + region", ["BK", "KFC", "roys", "CO_OWNED", "SOUTHJ", "CENTRALJ", "NORTHJ", "PA1", "GAP"]),
    ]
    rows = []
    for model, columns in models:
        result, _, _, _ = ols(sample, columns)
        result.insert(0, "model", model)
        rows.append(result)
    table4 = pd.concat(rows, ignore_index=True)

    extension_columns = [
        "BK", "KFC", "roys", "CO_OWNED", "SOUTHJ", "CENTRALJ", "NORTHJ", "PA1",
        "GAP", "GAP_CO_OWNED",
    ]
    extension_result, covariance, _, _ = ols(sample, extension_columns)
    extension_result.insert(0, "model", "Ownership heterogeneity")
    extension_result["N"] = len(sample)

    term_index = {term: i for i, term in enumerate(["constant", *extension_columns])}
    gap_i = term_index["GAP"]
    interaction_i = term_index["GAP_CO_OWNED"]
    franchise = float(extension_result.loc[extension_result.term.eq("GAP"), "coefficient"].iloc[0])
    company = franchise + float(extension_result.loc[extension_result.term.eq("GAP_CO_OWNED"), "coefficient"].iloc[0])
    company_var = covariance[gap_i, gap_i] + covariance[interaction_i, interaction_i] + 2 * covariance[gap_i, interaction_i]
    marginal = pd.DataFrame([
        {"quantity": "GAP effect, franchise stores", "estimate": franchise, "standard_error": math.sqrt(covariance[gap_i, gap_i])},
        {"quantity": "GAP effect, company-owned stores", "estimate": company, "standard_error": math.sqrt(company_var)},
    ])
    extension = pd.concat([
        extension_result.assign(quantity="coefficient"),
        marginal.assign(term="marginal_effect", model="Ownership heterogeneity", N=len(sample), SER=np.nan, R_squared=np.nan),
    ], ignore_index=True, sort=False)
    meta = {"table4_sample_n": int(len(sample)), "table4_sample_mean_change": float(sample["fte_change"].mean()), "table4_sample_sd_change": float(sample["fte_change"].std(ddof=1))}
    return table4, extension, meta


def normal_two_sided_p(t_stat: float) -> float:
    if not np.isfinite(t_stat):
        return float("nan")
    return float(math.erfc(abs(float(t_stat)) / math.sqrt(2.0)))


def robustness_checks(df: pd.DataFrame, table3_df: pd.DataFrame) -> pd.DataFrame:
    """Run transparent sensitivity checks around the published NJ-dummy model."""
    rows: list[dict] = []

    def add_model_row(check: str, specification: str, sample: pd.DataFrame, *, note: str):
        result, _, _, _ = ols(sample, ["STATE"], outcome="analysis_change")
        state = result.loc[result["term"].eq("STATE")].iloc[0]
        t_stat = float(state["t_stat"])
        rows.append({
            "check": check,
            "specification": specification,
            "sample_n": int(len(sample)),
            "estimate": float(state["coefficient"]),
            "standard_error": float(state["standard_error"]),
            "t_stat": t_stat,
            "normal_approx_p": normal_two_sided_p(t_stat),
            "permutation_p": np.nan,
            "note": note,
        })

    baseline = make_regression_sample(df)
    add_model_row(
        "Baseline",
        "NJ dummy; published Table 4 model (i)",
        baseline,
        note="Reference specification; conventional homoskedastic OLS SE.",
    )

    for weight in [0.4, 0.6]:
        alt = alternative_parttime_panel(df, weight)
        sample = make_regression_sample_for_columns(alt, "fte1_alt", "fte2_alt", "fte_change_alt")
        add_model_row(
            "Alternative part-time weight",
            f"NJ dummy; part-time weight={weight:.1f}",
            sample,
            note="Recomputes both waves and preserves the baseline sample screen.",
        )

    if "SHORE" in baseline.columns:
        add_model_row(
            "Geographic exclusion",
            "NJ dummy; exclude Shore stores",
            baseline.loc[baseline["SHORE"].eq(0)].copy(),
            note="Excludes observations flagged as Shore-area stores; coding follows supplied public data.",
        )
    if "NCALLS" in baseline.columns:
        add_model_row(
            "Survey follow-up exclusion",
            "NJ dummy; NCALLS <= 2",
            baseline.loc[baseline["NCALLS"].le(2)].copy(),
            note="Restricts to stores with at most two call attempts in the first survey wave.",
        )

    for chain, label in [(1, "Burger King"), (2, "KFC"), (3, "Roy Rogers"), (4, "Wendy's")]:
        add_model_row(
            "Leave-one-chain-out",
            f"NJ dummy; exclude {label}",
            baseline.loc[baseline["CHAIN"].ne(chain)].copy(),
            note="Tests whether the reduced-form estimate is driven by one restaurant chain.",
        )

    row5 = table3_df.loc[
        (table3_df["row"] == "5. Change in mean FTE, temporary closures set to zero")
        & (table3_df["stat"] == "estimate")
    ].iloc[0]
    row5_se = table3_df.loc[
        (table3_df["row"] == "5. Change in mean FTE, temporary closures set to zero")
        & (table3_df["stat"] == "standard_error")
    ].iloc[0]
    temp_t = float(row5["NJ-PA"] / row5_se["NJ-PA"])
    rows.append({
        "check": "Closure coding",
        "specification": "Difference-in-differences; temporary closures set to zero",
        "sample_n": int(df["fte_change_temp_as_zero"].notna().sum()),
        "estimate": float(row5["NJ-PA"]),
        "standard_error": float(row5_se["NJ-PA"]),
        "t_stat": temp_t,
        "normal_approx_p": normal_two_sided_p(temp_t),
        "permutation_p": np.nan,
        "note": "Table 3 row 5 sensitivity; temporary/renovation/highway/mall-fire closures are coded as zero employment.",
    })

    rng = np.random.default_rng(20261009)
    observed_result, _, _, _ = ols(baseline, ["STATE"])
    observed_beta = float(observed_result.loc[observed_result["term"].eq("STATE"), "coefficient"].iloc[0])
    permuted = np.empty(2000, dtype=float)
    states = baseline["STATE"].to_numpy(float)
    for i in range(len(permuted)):
        shuffled = rng.permutation(states)
        perm_sample = baseline.copy()
        perm_sample["permuted_state"] = shuffled
        permuted_result, _, _, _ = ols(perm_sample, ["permuted_state"])
        permuted[i] = float(permuted_result.loc[permuted_result["term"].eq("permuted_state"), "coefficient"].iloc[0])
    permutation_p = float((1 + np.sum(np.abs(permuted) >= abs(observed_beta))) / (len(permuted) + 1))
    observed_state = observed_result.loc[observed_result["term"].eq("STATE")].iloc[0]
    rows.append({
        "check": "Randomization inference",
        "specification": "NJ dummy; 2,000 state-label permutations",
        "sample_n": int(len(baseline)),
        "estimate": observed_beta,
        "standard_error": float(observed_state["standard_error"]),
        "t_stat": float(observed_state["t_stat"]),
        "normal_approx_p": normal_two_sided_p(float(observed_state["t_stat"])),
        "permutation_p": permutation_p,
        "note": "Permutation preserves the observed number of NJ stores; seed=20261009. This is a diagnostic, not a replacement for design-based inference.",
    })
    return pd.DataFrame(rows)


def wage_distribution_figure(df: pd.DataFrame, path: Path):
    image = Image.new("RGB", (1800, 1100), "white")
    draw = ImageDraw.Draw(image)
    title_font = font(36)
    subtitle_font = font(26)
    label_font = font(18)
    small_font = font(16)
    draw.text((70, 35), "Figure 1. Distribution of starting wage rates", fill="#14324a", font=title_font)

    wage_values = sorted(set(
        pd.concat([df["WAGE_ST"], df["WAGE_ST2"]]).dropna().round(2).tolist()
    ))
    states = [(1, "New Jersey", "#1f4e79"), (0, "Pennsylvania", "#c65d3c")]
    panels = [("Wave 1", "WAGE_ST", 130), ("Wave 2", "WAGE_ST2", 610)]
    max_pct = 0.0
    distributions = {}
    for _, column, _ in panels:
        for state, _, _ in states:
            z = df.loc[df["STATE"].eq(state), column].dropna().round(2)
            denom = len(z)
            distributions[(column, state)] = [100.0 * float((z == w).sum()) / denom for w in wage_values]
            max_pct = max(max_pct, max(distributions[(column, state)] or [0]))
    y_max = max(10, int(math.ceil(max_pct / 10.0) * 10))

    for panel_title, column, top in panels:
        x0, x1 = 130, 1690
        y0, y1 = top + 65, top + 390
        draw.text((x0, top), panel_title, fill="#14324a", font=subtitle_font)
        draw.rectangle((x0, y0, x1, y1), outline="#8799a8", width=2)
        for tick in range(0, y_max + 1, max(10, y_max // 5)):
            y = y1 - (y1 - y0) * tick / y_max
            draw.line((x0, y, x1, y), fill="#e2e8ed", width=1)
            draw.text((x0 - 48, y - 10), str(tick), fill="#4d5b65", font=small_font)
        slot = (x1 - x0) / max(1, len(wage_values))
        bar_width = max(4, int(slot * 0.30))
        for j, wage in enumerate(wage_values):
            center = x0 + slot * (j + 0.5)
            for offset, state in [(-bar_width * 0.65, 1), (bar_width * 0.65, 0)]:
                pct = distributions[(column, state)][j]
                height = (y1 - y0) * pct / y_max
                draw.rectangle((center + offset - bar_width / 2, y1 - height, center + offset + bar_width / 2, y1), fill=states[0 if state == 1 else 1][2])
            if j % max(1, len(wage_values) // 14) == 0:
                text = f"{wage:.2f}"
                draw.text((center - 24, y1 + 12), text, fill="#4d5b65", font=small_font)
        draw.text((x0, y1 + 48), "Starting wage ($ per hour)", fill="#4d5b65", font=label_font)
        draw.text((x1 - 290, y0 - 45), "NJ", fill=states[0][2], font=label_font)
        draw.text((x1 - 190, y0 - 45), "PA", fill=states[1][2], font=label_font)
    image.save(path)


def replication_comparison(table3_df: pd.DataFrame, table4_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    def add(label: str, original: float, replicated: float, note: str):
        rows.append({
            "result": label,
            "original_paper": original,
            "replicated": replicated,
            "difference": replicated - original,
            "note": note,
        })

    row3 = table3_df.loc[(table3_df["row"] == "3. Change in mean FTE") & (table3_df["stat"] == "estimate")].iloc[0]
    row4 = table3_df.loc[(table3_df["row"] == "4. Change in mean FTE, balanced sample") & (table3_df["stat"] == "estimate")].iloc[0]
    row5 = table3_df.loc[(table3_df["row"] == "5. Change in mean FTE, temporary closures set to zero") & (table3_df["stat"] == "estimate")].iloc[0]
    add("Table 3 row 3 DiD", 2.76, float(row3["NJ-PA"]), "Unbalanced means")
    add("Table 3 row 4 DiD", 2.75, float(row4["NJ-PA"]), "Balanced employment sample")
    add("Table 3 row 5 DiD", 2.51, float(row5["NJ-PA"]), "Temporary closures set to zero")

    mapping = [
        ("(i) NJ dummy", "STATE", 2.33),
        ("(ii) NJ dummy + chain/ownership", "STATE", 2.30),
        ("(iii) GAP", "GAP", 15.65),
        ("(iv) GAP + chain/ownership", "GAP", 14.92),
        ("(v) GAP + chain/ownership + region", "GAP", 11.91),
    ]
    for model, term, original in mapping:
        replicated = float(table4_df.loc[(table4_df["model"] == model) & (table4_df["term"] == term), "coefficient"].iloc[0])
        note = "Published model; conventional OLS standard errors"
        if model.startswith("(v)"):
            note += "; small difference remains in region-control specification"
        add(f"Table 4 {model} {term}", original, replicated, note)
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Replicate Card and Krueger (1994) from public.csv.")
    parser.add_argument("--input", required=True, help="Path to the course-provided public.csv")
    parser.add_argument("--output", default=str(Path(__file__).resolve().parents[1] / "outputs"), help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    processed_dir = output_dir.parent / "data" / "processed"
    for path in [tables_dir, figures_dir, processed_dir]:
        path.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(input_path)
    if raw.shape != (410, 46):
        raise ValueError(f"Expected 410 rows and 46 columns, found {raw.shape}.")
    df = add_derived_variables(raw)

    df.to_csv(processed_dir / "analysis_panel.csv", index=False)
    table2(df).to_csv(tables_dir / "table2.csv", index=False)
    table3_df, table3_validation = table3(df)
    table3_df.to_csv(tables_dir / "table3.csv", index=False)
    table4_df, extension_df, table4_meta = table4_and_extension(df)
    table4_df.to_csv(tables_dir / "table4.csv", index=False)
    extension_df.to_csv(tables_dir / "extension_ownership_heterogeneity.csv", index=False)
    replication_comparison(table3_df, table4_df).to_csv(tables_dir / "replication_comparison.csv", index=False)
    robustness_df = robustness_checks(df, table3_df)
    robustness_df.to_csv(tables_dir / "robustness_checks.csv", index=False)
    wage_distribution_figure(df, figures_dir / "figure1.png")

    status_counts = df["STATUS2"].value_counts().sort_index().to_dict()
    checks = {
        "input_file": str(input_path),
        "rows": int(len(df)),
        "columns": int(raw.shape[1]),
        "NJ_rows": int(df["STATE"].eq(1).sum()),
        "PA_rows": int(df["STATE"].eq(0).sum()),
        "duplicate_original_SHEET_rows": int(df["SHEET"].duplicated().sum()),
        "fte1_available": int(df["fte1"].notna().sum()),
        "fte2_available": int(df["fte2"].notna().sum()),
        "balanced_fte_rows": int((df["fte1"].notna() & df["fte2"].notna()).sum()),
        "status2_counts": ";".join(f"{k}:{v}" for k, v in status_counts.items()),
        **table3_validation,
        **table4_meta,
    }
    pd.DataFrame([checks]).to_csv(tables_dir / "validation_checks.csv", index=False)
    print(pd.Series(checks).to_string())
    print(f"\nWrote results to: {output_dir}")


if __name__ == "__main__":
    main()
