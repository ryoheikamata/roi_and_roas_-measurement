# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# import japanize_matplotlib
#
# st.title("費用対効果シミュレーション（概算版）")
#
# st.sidebar.header("基本パラメータ")
# months = st.sidebar.number_input("シミュレーション期間（月）", value=12, min_value=1, max_value=24)
#
# # 商品やブランドの単価・広告費などの想定
# product_price = st.sidebar.number_input("商品単価 or 平均客単価 (円)", value=5000)
# monthly_sales = st.sidebar.number_input("月間売上 (万円)", value=800)  # 例：800万円
# monthly_ad_cost = st.sidebar.number_input("月間広告費 (万円)", value=80)  # 例：80万円
# ad_sales_ratio = st.sidebar.slider("広告経由売上の割合（%）", 0, 100, 50)  # 例：50%
# target_roas = st.sidebar.number_input("目標ROAS（広告費→売上の倍率）", value=5.0)
#
# # コンサル費用などの固定費想定
# monthly_consulting_fee = st.sidebar.number_input("コンサル費用 (万円)", value=30)
# other_fixed_cost = st.sidebar.number_input("その他固定費 (万円)", value=20)
#
# # 割引率（NPV/IRR計算用）
# discount_rate_annual = st.sidebar.number_input("割引率（年間 %）", value=5) / 100
#
# st.sidebar.markdown("""
# このサンプルは、
# - **月間売上**と**広告費**をざっくり入力
# - **広告経由売上**の割合、**目標ROAS**を指定
# - **コンサル費**などの固定費を差し引いて
# **月ごとの利益やROIを試算**します。
#
# あくまで概算シミュレーションです。
# """)
#
# # ----------------------
# # シナリオの前提ロジック
# # ----------------------
# # 例として、毎月売上が徐々に上がる or 下がる などの変動を入れたい場合はここで処理を追加
# # ここでは、全月「月間売上 = monthly_sales」固定とし、必要があればユーザーがシミュレーション期間中に
# # 値を調整できるようにするか、または何らかの成長率を掛けるなどの工夫も可能
#
# # 広告経由売上
# ad_sales = monthly_sales * (ad_sales_ratio / 100.0)
#
# # 広告経由売上から計算した実際のROAS
# # ROAS = (広告経由売上) / (広告費)
# actual_roas = (ad_sales / monthly_ad_cost) if monthly_ad_cost != 0 else 0
#
# # 月次の利益計算： (月間売上) - (広告費) - (コンサル費用) - (その他固定費)
# # ※ 仕入原価や楽天手数料、物流費など、さらに項目を増やしたい場合はここに加算・減算
# monthly_profit = monthly_sales - monthly_ad_cost - monthly_consulting_fee - other_fixed_cost
#
# # 12ヶ月 or 指定期間分のリストを作る
# sales_list = []
# ad_cost_list = []
# ad_sales_list = []
# roas_list = []
# profit_list = []
# for m in range(1, months + 1):
#     # 今回は全月同じ値とする
#     s = monthly_sales
#     ad = monthly_ad_cost
#     ads = ad_sales
#     roas = ads / ad if ad else 0
#     p = s - ad - monthly_consulting_fee - other_fixed_cost
#
#     sales_list.append(s)
#     ad_cost_list.append(ad)
#     ad_sales_list.append(ads)
#     roas_list.append(roas)
#     profit_list.append(p)
#
# # 累積利益
# cum_profit = pd.Series(profit_list).cumsum()
#
# # DataFrame化
# df = pd.DataFrame({
#     "月": [f"{i}月" for i in range(1, months + 1)],
#     "売上 (万円)": sales_list,
#     "広告費 (万円)": ad_cost_list,
#     "広告経由売上 (万円)": ad_sales_list,
#     "ROAS": roas_list,
#     "利益 (万円)": profit_list,
#     "累積利益 (万円)": cum_profit
# })
#
# st.subheader("月次シミュレーション結果")
# st.dataframe(
#     df.style.format("{:.1f}", subset=["売上 (万円)", "広告費 (万円)", "広告経由売上 (万円)", "ROAS", "利益 (万円)", "累積利益 (万円)"])
# )
#
#
# # ----------------------
# # 投資対効果指標
# # ----------------------
#
# # ROI: (総利益 / 総投資額) * 100
# # 投資額として、コンサル費用+その他固定費+広告費 などをどこまで含めるかは定義次第
# # ここでは (広告費 + コンサル費 + その他固定費) * months を投資額とする例
# total_profit = sum(profit_list)
# total_investment = (monthly_ad_cost + monthly_consulting_fee + other_fixed_cost) * months
# roi = (total_profit / total_investment) * 100 if total_investment != 0 else 0
#
# # NPV / IRR用に、将来キャッシュフロー(ここでは「利益」)を割引
# def calc_npv(rate, cash_flows):
#     val = 0.0
#     for i, cf in enumerate(cash_flows):
#         val += cf / ((1 + rate) ** i)
#     return val
#
# def calc_irr(cash_flows, guess=0.1, tol=1e-6, max_iter=1000):
#     rate = guess
#     for _ in range(max_iter):
#         npv_val = calc_npv(rate, cash_flows)
#         epsilon = 1e-6
#         derivative = (calc_npv(rate + epsilon, cash_flows) - calc_npv(rate - epsilon, cash_flows)) / (2*epsilon)
#         if derivative == 0:
#             break
#         new_rate = rate - npv_val / derivative
#         if abs(new_rate - rate) < tol:
#             return new_rate
#         rate = new_rate
#     return rate
#
# # 年間割引率を月次に変換
# monthly_discount = (1 + discount_rate_annual) ** (1/12) - 1
# # キャッシュフロー: 初期投資を - (初期費用など) として扱うケースもあるが、ここでは簡易化
# # 0から始めて各月の利益をCFとする
# cash_flows = [0] + profit_list
# npv_val = calc_npv(monthly_discount, cash_flows)
# irr_monthly = calc_irr(cash_flows)
# irr_annual = (1 + irr_monthly)**12 - 1 if irr_monthly else None
#
# # Payback Period（何ヶ月で累積利益が0を超えるか）
# break_even_month = None
# for i, cp in enumerate(cum_profit, start=1):
#     if cp >= 0:
#         break_even_month = i
#         break
#
# st.subheader("投資対効果指標")
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("総利益 (万円)", f"{total_profit:.1f}")
# col2.metric("総投資額 (万円)", f"{total_investment:.1f}")
# col3.metric("ROI (%)", f"{roi:.1f}")
# if irr_annual is not None:
#     col4.metric("IRR (年間)", f"{irr_annual*100:.1f}%")
# else:
#     col4.metric("IRR (年間)", "計算不能")
#
# st.markdown(f"**NPV**： {npv_val:.1f} 万円")
#
# if break_even_month:
#     st.success(f"損益分岐点（投資回収）は {break_even_month}ヶ月目 です。")
# else:
#     st.warning("12ヶ月以内に損益分岐点に到達しません。")
#
# # グラフ表示（累積利益など）
# fig, ax = plt.subplots(figsize=(8,4))
# ax.plot(range(1, months+1), cum_profit, marker="o", label="累積利益")
# ax.axhline(0, color="red", linestyle="--", label="損益分岐点")
# ax.set_xlabel("月")
# ax.set_ylabel("累積利益 (万円)")
# ax.set_title("累積利益の推移")
# ax.legend()
# st.pyplot(fig)
#
# # 目標ROASとの比較
# if actual_roas >= target_roas:
#     st.info(f"現在のROAS（{actual_roas:.2f}）は目標（{target_roas}）を上回っています。")
# else:
#     st.warning(f"現在のROAS（{actual_roas:.2f}）は目標（{target_roas}）を下回っています。広告戦略を要検討。")


# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# import japanize_matplotlib
#
# st.title("楽天運用コンサル 費用対効果シミュレーション（詳細版・月別変動版）")
#
# st.sidebar.header("基本パラメータ")
# months = st.sidebar.number_input("シミュレーション期間（月）", value=12, min_value=1, max_value=24)
#
# base_sales = st.sidebar.number_input("基準月間売上 (万円)", value=800)
# base_ad_cost = st.sidebar.number_input("基準月間広告費 (万円)", value=80)
#
# # 動的変化の倍率設定
# april_ad_cost_multiplier = st.sidebar.number_input("4月の広告費増加倍率", value=1.5)
# may_sales_multiplier = st.sidebar.number_input("5月の売上増加倍率", value=1.2)
#
# # 固定費
# monthly_consulting_fee = st.sidebar.number_input("コンサル費用 (万円)", value=30)
# store_fee = st.sidebar.number_input("楽天出店費用 (万円/月)", value=40)
# fixed_cost = monthly_consulting_fee + store_fee
#
# st.sidebar.markdown("""
# **前提条件：**
# - 売上は基準値を使用。
# - **4月**は広告費が通常の倍率（例：1.5倍）になる。
# - **5月**は売上が通常の倍率（例：1.2倍）になる。
# - 他の月は基準値となります。
# - 以下の費用割合で各項目を計算します。
# """)
#
# # 費用割合（%）
# cogs_ratio = st.sidebar.number_input("仕入原価割合 (%)", value=70) / 100  # 70%
# rakuten_fee_ratio = st.sidebar.number_input("楽天手数料割合 (%)", value=8) / 100  # 8%
# logistics_ratio = st.sidebar.number_input("物流費割合 (%)", value=10) / 100  # 10%
# coupon_ratio = st.sidebar.number_input("クーポン原資割合 (%)", value=3) / 100  # 3%
# point_ratio = st.sidebar.number_input("ポイント還元割合 (%)", value=2) / 100  # 2%
# ad_cost_ratio = st.sidebar.number_input("広告費割合 (%)", value=10) / 100  # 10%
#
# # シナリオ条件により各月の数値を動的に変更
# sales_list = []
# ad_cost_list = []
# cogs_list = []
# rakuten_fee_list = []
# logistics_list = []
# coupon_list = []
# point_list = []
# variable_cost_total = []
# profit_list = []
# roas_list = []
#
# for m in range(1, months + 1):
#     # 売上: 5月は増加倍率を適用
#     sales_multiplier = 1.0
#     if m == 5:
#         sales_multiplier = may_sales_multiplier
#     sales = base_sales * sales_multiplier
#
#     # 広告費: 4月は増加倍率を適用
#     ad_multiplier = 1.0
#     if m == 4:
#         ad_multiplier = april_ad_cost_multiplier
#     ad_cost = base_ad_cost * ad_multiplier
#
#     # 各費用項目
#     cogs = sales * cogs_ratio
#     rakuten_fee = sales * rakuten_fee_ratio
#     logistics = sales * logistics_ratio
#     coupon = sales * coupon_ratio
#     point = sales * point_ratio
#
#     # 変動費合計： 広告費 + 楽天手数料 + 物流費 + クーポン原資 + ポイント還元
#     var_cost = ad_cost + rakuten_fee + logistics + coupon + point
#
#     # 売上から仕入原価を引いた粗利益
#     gross_profit = sales - cogs
#     # 月次利益 = 粗利益 - (その他変動費： 広告費＋楽天手数料＋物流費＋クーポン＋ポイント) - 固定費
#     profit = gross_profit - (rakuten_fee + logistics + coupon + point + ad_cost) - fixed_cost
#
#     # ROAS = 売上 / 広告費（単位：倍率）
#     roas = sales / ad_cost if ad_cost != 0 else 0
#
#     sales_list.append(sales)
#     ad_cost_list.append(ad_cost)
#     cogs_list.append(cogs)
#     rakuten_fee_list.append(rakuten_fee)
#     logistics_list.append(logistics)
#     coupon_list.append(coupon)
#     point_list.append(point)
#     variable_cost_total.append(var_cost)
#     profit_list.append(profit)
#     roas_list.append(roas)
#
# # 累積利益
# cum_profit = pd.Series(profit_list).cumsum()
#
# # DataFrame作成
# df = pd.DataFrame({
#     "月": [f"{m}月" for m in range(1, months + 1)],
#     "売上 (万円)": sales_list,
#     "広告費 (万円)": ad_cost_list,
#     "仕入原価 (万円)": cogs_list,
#     "楽天手数料 (万円)": rakuten_fee_list,
#     "物流費 (万円)": logistics_list,
#     "クーポン原資 (万円)": coupon_list,
#     "ポイント還元 (万円)": point_list,
#     "変動費合計 (万円)": variable_cost_total,
#     "固定費 (万円)": [fixed_cost] * months,
#     "利益 (万円)": profit_list,
#     "累積利益 (万円)": cum_profit,
#     "ROAS": roas_list
# })
#
# st.subheader("月次シミュレーション結果")
# st.dataframe(df.style.format({
#     "売上 (万円)": "{:.1f}",
#     "広告費 (万円)": "{:.1f}",
#     "仕入原価 (万円)": "{:.1f}",
#     "楽天手数料 (万円)": "{:.1f}",
#     "物流費 (万円)": "{:.1f}",
#     "クーポン原資 (万円)": "{:.1f}",
#     "ポイント還元 (万円)": "{:.1f}",
#     "変動費合計 (万円)": "{:.1f}",
#     "固定費 (万円)": "{:.1f}",
#     "利益 (万円)": "{:.1f}",
#     "累積利益 (万円)": "{:.1f}",
#     "ROAS": "{:.2f}"
# }))
#
# # 投資対効果指標
# # 総利益は profit_list の合計
# total_profit = sum(profit_list)
# # 総投資額は、固定費＋広告費の合計（月毎）を採用
# total_investment = sum([fixed_cost + ad for ad in ad_cost_list])
# roi = (total_profit / total_investment) * 100 if total_investment != 0 else 0
#
# # 損益分岐点（累積利益が0以上になる最初の月）
# break_even_month = None
# for m, cp in enumerate(cum_profit, start=1):
#     if cp >= 0:
#         break_even_month = m
#         break
#
# st.subheader("投資対効果指標")
# col1, col2, col3 = st.columns(3)
# col1.metric("総利益 (万円)", f"{total_profit:.1f}")
# col2.metric("総投資額 (万円)", f"{total_investment:.1f}")
# col3.metric("ROI (%)", f"{roi:.1f}")
#
# if break_even_month:
#     st.success(f"損益分岐点（投資回収）は {break_even_month}ヶ月目 です。")
# else:
#     st.warning("シミュレーション期間内に損益分岐点に到達していません。")
#
# # 累積利益のグラフ
# fig, ax = plt.subplots(figsize=(8, 4))
# ax.plot(range(1, months + 1), cum_profit, marker="o", label="累積利益")
# ax.axhline(0, color="red", linestyle="--", label="損益分岐点")
# ax.set_xlabel("月")
# ax.set_ylabel("累積利益 (万円)")
# ax.set_title("累積利益の推移")
# ax.legend()
# st.pyplot(fig)
#
# # 目標ROASとの比較（目標ROASはサイドバーで指定）
# target_roas = st.sidebar.number_input("目標ROAS", value=5.0)
# actual_avg_roas = np.mean(roas_list)
# if actual_avg_roas >= target_roas:
#     st.info(f"平均ROAS ({actual_avg_roas:.2f}) は目標 ({target_roas}) を上回っています。")
# else:
#     st.warning(f"平均ROAS ({actual_avg_roas:.2f}) は目標 ({target_roas}) を下回っています。")


# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import japanize_matplotlib
#
# st.title("Amazonコンサル導入シミュレーション")
#
# st.sidebar.header("基本パラメータ")
# months = st.sidebar.number_input("シミュレーション期間 (月)", value=12, min_value=1, max_value=36)
#
# # 現状のAmazon売上
# current_amz_sales = st.sidebar.number_input("現状Amazon月間売上 (円)", value=50000)
# # 月額コンサル費用
# consulting_fee = st.sidebar.number_input("コンサル費用 (円/月)", value=300000)
# # 広告費（導入後に使う想定）
# ad_budget = st.sidebar.number_input("広告費 (円/月)", value=50000)
#
# st.sidebar.markdown("""
# ### 売上成長シナリオ
# - **成長開始月**：導入後、効果が出るまでのラグ（月数）
# - **最終的な売上目標**：何か月目までにどの程度売上が伸びるか
# """)
#
# # 効果発現までのラグ
# lag_months = st.sidebar.number_input("効果発現までの月数", value=3, min_value=0)
# # 最終的な売上目標（12ヶ月後など）
# target_amz_sales = st.sidebar.number_input("導入後の目標月間売上 (円)", value=300000)
#
# st.sidebar.markdown("""
# **費用項目**
# Amazon手数料やFBA費用など、さらに細かい費用を入れる場合は下記で設定。
# """)
# # Amazon手数料率など
# amazon_fee_ratio = st.sidebar.slider("Amazon手数料率 (%)", 0, 30, 10)
# fba_fee_ratio = st.sidebar.slider("FBA手数料率 (%)", 0, 30, 5)
#
# st.sidebar.markdown("""
# **利益計算：**
# 売上 － (Amazon手数料+FBA手数料) － 広告費 － コンサル費
# """)
#
# # ---------------------------
# # シミュレーションロジック
# # ---------------------------
# sales_list = []
# fee_list = []
# profit_list = []
#
#
# # 月ごとに売上を補間して徐々に成長させる簡易モデル
# # 例）lag_monthsまでは現状売上、そこから target_amz_sales に向けて線形で伸びる
# def interpolate_sales(m, lag, current, target, total_months):
#     if m <= lag:
#         return current
#     else:
#         # lag以降～最終月にかけて売上が target に向けて線形に伸びる
#         # 例：lag+1ヶ月目→lag+2ヶ月目→…→total_months
#         #    m-lag を使って伸び率を算出
#         growth_span = total_months - lag  # 成長期間
#         progress = (m - lag) / growth_span  # 0→1に線形で増加
#         return current + (target - current) * progress
#
#
# for m in range(1, months + 1):
#     # 売上計算
#     monthly_sales = interpolate_sales(m, lag_months, current_amz_sales, target_amz_sales, months)
#
#     # Amazon手数料＋FBA手数料
#     fee = monthly_sales * (amazon_fee_ratio + fba_fee_ratio) / 100.0
#
#     # 月次利益
#     # 広告費 ad_budget を導入後ずっとかける想定（初月からかける場合）
#     monthly_profit = monthly_sales - fee - ad_budget - consulting_fee
#
#     sales_list.append(monthly_sales)
#     fee_list.append(fee)
#     profit_list.append(monthly_profit)
#
# # 累積利益
# cum_profit = pd.Series(profit_list).cumsum()
#
# df = pd.DataFrame({
#     "月": [f"{i}月" for i in range(1, months + 1)],
#     "売上 (円)": sales_list,
#     "Amazon手数料 (円)": fee_list,
#     "広告費 (円)": [ad_budget] * months,
#     "コンサル費 (円)": [consulting_fee] * months,
#     "利益 (円)": profit_list,
#     "累積利益 (円)": cum_profit
# })
#
# st.subheader("月次シミュレーション結果")
# # 数値列だけフォーマット
# st.dataframe(
#     df.style.format({
#         "売上 (円)": "{:,.0f}",
#         "Amazon手数料 (円)": "{:,.0f}",
#         "広告費 (円)": "{:,.0f}",
#         "コンサル費 (円)": "{:,.0f}",
#         "利益 (円)": "{:,.0f}",
#         "累積利益 (円)": "{:,.0f}",
#     })
# )
#
# # ROI (総利益 / 総投資額)
# # 投資額：広告費 + コンサル費 の総額
# total_profit = sum(profit_list)
# total_investment = (ad_budget + consulting_fee) * months
# roi = (total_profit / total_investment) * 100 if total_investment != 0 else 0
#
# # 損益分岐点（Payback Point）
# break_even_month = None
# for i, cp in enumerate(cum_profit, start=1):
#     if cp >= 0:
#         break_even_month = i
#         break
#
# st.subheader("投資対効果指標")
# col1, col2 = st.columns(2)
# col1.metric("総利益 (円)", f"{total_profit:,.0f}")
# col2.metric("ROI (%)", f"{roi:,.1f}")
#
# if break_even_month:
#     st.success(f"損益分岐点は {break_even_month}ヶ月目 です。")
# else:
#     st.warning("シミュレーション期間内に損益分岐点に到達しません。")
#
# # 累積利益グラフ
# fig, ax = plt.subplots(figsize=(7, 4))
# ax.plot(range(1, months + 1), cum_profit, marker="o", label="累積利益")
# ax.axhline(0, color="red", linestyle="--", label="損益分岐点")
# ax.set_xlabel("月")
# ax.set_ylabel("累積利益 (円)")
# ax.set_title("累積利益の推移")
# ax.legend()
# st.pyplot(fig)


#
# import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import japanize_matplotlib
#
# st.title("費用対効果シミュレーション")
#
# # ------------------------------------
# # 共通の設定（表示上など）
# # ------------------------------------
# st.sidebar.header("共通設定")
# months = st.sidebar.number_input("シミュレーション期間 (月)", value=12, min_value=1, max_value=36)
# consulting_fee = st.sidebar.number_input("コンサル費用 (円/月)", value=300000)
#
# # ------------------------------------
# # タブを用いて Amazon / 楽天 切り替え
# # ------------------------------------
# tab1, tab2 = st.tabs(["Amazon", "楽天"])
#
# # ------------------------------------
# # Amazonタブ
# # ------------------------------------
# with tab1:
#     st.subheader("【Amazon】シミュレーション")
#
#     # サイドバーにAmazon固有の設定
#     st.sidebar.subheader("Amazon設定")
#     base_sales_amz = st.sidebar.number_input("Amazon現状月間売上 (円)", value=50000)
#     # 月ごとの広告費を個別に入力
#     st.sidebar.markdown("#### 月ごとのAmazon広告費を入力")
#     ad_cost_amz = []
#     for m in range(1, months+1):
#         val = st.sidebar.number_input(f"Amazon {m}月の広告費 (円)", value=0, key=f"amz_ad_{m}")
#         ad_cost_amz.append(val)
#
#     # Amazon手数料など
#     amazon_fee_ratio = st.sidebar.slider("Amazon手数料率 (%)", 0, 30, 10)
#     fba_fee_ratio = st.sidebar.slider("FBA手数料率 (%)", 0, 30, 5)
#
#     # 売上増加率をざっくり入力して月ごとに売上が伸びる想定
#     st.sidebar.markdown("#### Amazon売上成長シナリオ")
#     growth_rate_amz = st.sidebar.number_input("月ごとの売上成長率 (%)", value=10)
#
#     # ---- シミュレーション実行 ----
#     sales_list = []
#     profit_list = []
#     fee_list = []
#
#     current_sales = base_sales_amz
#     for m in range(1, months+1):
#         # 月ごとの売上（前月比 + growth_rate_amz%）
#         if m == 1:
#             monthly_sales = current_sales
#         else:
#             monthly_sales = sales_list[-1] * (1 + growth_rate_amz / 100.0)
#
#         # Amazon手数料 + FBA費用
#         fee = monthly_sales * (amazon_fee_ratio + fba_fee_ratio) / 100.0
#         # 利益 = 売上 - (手数料) - (広告費) - (コンサル費)
#         monthly_profit = monthly_sales - fee - ad_cost_amz[m-1] - consulting_fee
#
#         sales_list.append(monthly_sales)
#         fee_list.append(fee)
#         profit_list.append(monthly_profit)
#
#     cum_profit = pd.Series(profit_list).cumsum()
#
#     df_amz = pd.DataFrame({
#         "月": [f"{i}月" for i in range(1, months+1)],
#         "売上 (円)": sales_list,
#         "Amazon手数料 (円)": fee_list,
#         "広告費 (円)": ad_cost_amz,
#         "コンサル費 (円)": [consulting_fee]*months,
#         "利益 (円)": profit_list,
#         "累積利益 (円)": cum_profit
#     })
#
#     st.dataframe(
#         df_amz.style.format({
#             "売上 (円)": "{:,.0f}",
#             "Amazon手数料 (円)": "{:,.0f}",
#             "広告費 (円)": "{:,.0f}",
#             "コンサル費 (円)": "{:,.0f}",
#             "利益 (円)": "{:,.0f}",
#             "累積利益 (円)": "{:,.0f}",
#         })
#     )
#
#     # 投資対効果指標
#     total_profit_amz = sum(profit_list)
#     total_investment_amz = sum(ad_cost_amz) + consulting_fee * months
#     roi_amz = (total_profit_amz / total_investment_amz)*100 if total_investment_amz else 0
#
#     # 損益分岐点
#     break_even_amz = None
#     for i, cp in enumerate(cum_profit, start=1):
#         if cp >= 0:
#             break_even_amz = i
#             break
#
#     st.markdown("#### 投資対効果指標（Amazon）")
#     col1, col2 = st.columns(2)
#     col1.metric("総利益 (円)", f"{total_profit_amz:,.0f}")
#     col2.metric("ROI (%)", f"{roi_amz:,.1f}")
#
#     if break_even_amz:
#         st.success(f"損益分岐点： {break_even_amz}ヶ月目")
#     else:
#         st.warning("期間内に損益分岐点に到達しません。")
#
#     fig_amz, ax_amz = plt.subplots(figsize=(6,3))
#     ax_amz.plot(range(1, months+1), cum_profit, marker="o", label="累積利益")
#     ax_amz.axhline(0, color="red", linestyle="--", label="損益分岐点")
#     ax_amz.set_xlabel("月")
#     ax_amz.set_ylabel("累積利益 (円)")
#     ax_amz.set_title("Amazon：累積利益推移")
#     ax_amz.legend()
#     st.pyplot(fig_amz)
#
#
# # ------------------------------------
# # 楽天タブ
# # ------------------------------------
# with tab2:
#     st.subheader("【楽天】シミュレーション")
#
#     # サイドバーに楽天固有の設定
#     st.sidebar.subheader("楽天設定")
#     base_sales_rkt = st.sidebar.number_input("楽天現状月間売上 (円)", value=100000, key="rkt_base_sales")
#     st.sidebar.markdown("#### 月ごとの楽天広告費を入力")
#     ad_cost_rkt = []
#     for m in range(1, months+1):
#         val = st.sidebar.number_input(f"楽天 {m}月の広告費 (円)", value=0, key=f"rkt_ad_{m}")
#         ad_cost_rkt.append(val)
#
#     # 楽天手数料など
#     r_fee_ratio = st.sidebar.slider("楽天手数料率 (%)", 0, 30, 8, key="rkt_fee_slider")
#     logistics_ratio = st.sidebar.slider("物流費率 (%)", 0, 30, 10, key="rkt_logi_slider")
#
#     # 売上成長率
#     st.sidebar.markdown("#### 楽天売上成長シナリオ")
#     growth_rate_rkt = st.sidebar.number_input("月ごとの売上成長率(楽天) (%)", value=5, key="rkt_growth")
#
#     # ---- シミュレーション実行 ----
#     sales_list_rkt = []
#     fee_list_rkt = []
#     profit_list_rkt = []
#
#     current_sales_rkt = base_sales_rkt
#     for m in range(1, months+1):
#         if m == 1:
#             monthly_sales_rkt = current_sales_rkt
#         else:
#             monthly_sales_rkt = sales_list_rkt[-1] * (1 + growth_rate_rkt / 100.0)
#
#         # 楽天手数料 + 物流費
#         fee_rkt = monthly_sales_rkt * (r_fee_ratio + logistics_ratio) / 100.0
#
#         # 利益 = 売上 - 手数料 - 広告費 - コンサル費
#         monthly_profit_rkt = monthly_sales_rkt - fee_rkt - ad_cost_rkt[m-1] - consulting_fee
#
#         sales_list_rkt.append(monthly_sales_rkt)
#         fee_list_rkt.append(fee_rkt)
#         profit_list_rkt.append(monthly_profit_rkt)
#
#     cum_profit_rkt = pd.Series(profit_list_rkt).cumsum()
#
#     df_rkt = pd.DataFrame({
#         "月": [f"{i}月" for i in range(1, months+1)],
#         "売上 (円)": sales_list_rkt,
#         "楽天手数料+物流費 (円)": fee_list_rkt,
#         "広告費 (円)": ad_cost_rkt,
#         "コンサル費 (円)": [consulting_fee]*months,
#         "利益 (円)": profit_list_rkt,
#         "累積利益 (円)": cum_profit_rkt
#     })
#
#     st.dataframe(
#         df_rkt.style.format({
#             "売上 (円)": "{:,.0f}",
#             "楽天手数料+物流費 (円)": "{:,.0f}",
#             "広告費 (円)": "{:,.0f}",
#             "コンサル費 (円)": "{:,.0f}",
#             "利益 (円)": "{:,.0f}",
#             "累積利益 (円)": "{:,.0f}",
#         })
#     )
#
#     # 投資対効果指標
#     total_profit_rkt = sum(profit_list_rkt)
#     total_investment_rkt = sum(ad_cost_rkt) + consulting_fee * months
#     roi_rkt = (total_profit_rkt / total_investment_rkt)*100 if total_investment_rkt else 0
#
#     # 損益分岐点
#     break_even_rkt = None
#     for i, cp in enumerate(cum_profit_rkt, start=1):
#         if cp >= 0:
#             break_even_rkt = i
#             break
#
#     st.markdown("#### 投資対効果指標（楽天）")
#     col1, col2 = st.columns(2)
#     col1.metric("総利益 (円)", f"{total_profit_rkt:,.0f}")
#     col2.metric("ROI (%)", f"{roi_rkt:,.1f}")
#
#     if break_even_rkt:
#         st.success(f"損益分岐点： {break_even_rkt}ヶ月目")
#     else:
#         st.warning("期間内に損益分岐点に到達しません。")
#
#     fig_rkt, ax_rkt = plt.subplots(figsize=(6,3))
#     ax_rkt.plot(range(1, months+1), cum_profit_rkt, marker="o", label="累積利益")
#     ax_rkt.axhline(0, color="red", linestyle="--", label="損益分岐点")
#     ax_rkt.set_xlabel("月")
#     ax_rkt.set_ylabel("累積利益 (円)")
#     ax_rkt.set_title("楽天：累積利益推移")
#     ax_rkt.legend()
#     st.pyplot(fig_rkt)

#
# import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import japanize_matplotlib
# import datetime
# import altair as alt
#
# # ページ設定
# st.set_page_config(
#     page_title="EC投資対効果シミュレーター",
#     page_icon="💹",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )
#
# # カスタムCSS
# st.markdown("""
# <style>
#     .main .block-container {padding-top: 2rem;}
#     h1 {margin-bottom: 0.5rem;}
#     .stTabs [data-baseweb="tab-list"] {gap: 2rem;}
#     .stTabs [data-baseweb="tab"] {height: 3rem;}
#     .metric-card {
#         background-color: #f8f9fa;
#         border-radius: 0.5rem;
#         padding: 1rem;
#         box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
#         margin-bottom: 1rem;
#     }
#     /* ヘルプ情報のスタイル */
#     .help-box {
#         background-color: #f1f8ff;
#         border-left: 5px solid #0366d6;
#         padding: 1rem;
#         border-radius: 0.3rem;
#         margin-bottom: 1rem;
#     }
#     /* ボタンのスタイル強化 */
#     .stButton>button {
#         background-color: #0366d6;
#         color: white;
#         border-radius: 0.3rem;
#         padding: 0.5rem 1rem;
#         border: none;
#     }
#     .stButton>button:hover {
#         background-color: #0353b4;
#     }
#     /* ダウンロードボタンのスタイル */
#     .stDownloadButton>button {
#         background-color: #28a745;
#         color: white;
#     }
#     .stDownloadButton>button:hover {
#         background-color: #218838;
#     }
# </style>
# """, unsafe_allow_html=True)
#
# # 業界別のデフォルト値（成長率、ROAS等）
# industry_defaults = {
#     "食品・飲料": {"growth_rate": 15, "roas": 350, "profit_margin": 40},
#     "美容・化粧品": {"growth_rate": 20, "roas": 400, "profit_margin": 60},
#     "アパレル": {"growth_rate": 18, "roas": 320, "profit_margin": 45},
#     "家電・デジタル": {"growth_rate": 12, "roas": 280, "profit_margin": 25},
#     "日用品・生活雑貨": {"growth_rate": 10, "roas": 300, "profit_margin": 35},
#     "その他": {"growth_rate": 15, "roas": 300, "profit_margin": 40}
# }
#
# # モール別の手数料率デフォルト値
# mall_fee_defaults = {
#     "Amazon": 15,
#     "楽天": 13,
#     "Yahoo!ショッピング": 12,
#     "自社EC": 5
# }
#
#
# # 広告費配分パターンの関数
# def calculate_ad_cost_by_pattern(pattern, total_budget, months, start_ratio=0.5):
#     monthly_costs = []
#
#     if pattern == "均等配分":
#         # 毎月同じ金額
#         monthly_budget = total_budget / months
#         monthly_costs = [monthly_budget] * months
#
#     elif pattern == "前半重点型":
#         # 前半(1-3ヶ月)に予算の60%を投入、その後減少
#         front_months = min(3, months)
#         front_budget = total_budget * 0.6
#         front_monthly = front_budget / front_months
#
#         remaining_budget = total_budget - front_budget
#         remaining_months = months - front_months
#         back_monthly = remaining_budget / remaining_months if remaining_months > 0 else 0
#
#         monthly_costs = [front_monthly] * front_months + [back_monthly] * remaining_months
#
#     elif pattern == "段階的増加型":
#         # 徐々に予算を増やしていく
#         step = 2 * total_budget / (months * (months + 1))  # 等差数列の和の公式から計算
#         monthly_costs = [step * (i + 1) for i in range(months)]
#
#     elif pattern == "後半重点型":
#         # 後半に予算の60%を投入
#         back_months = min(3, months)
#         back_budget = total_budget * 0.6
#         back_monthly = back_budget / back_months if back_months > 0 else 0
#
#         remaining_budget = total_budget - back_budget
#         remaining_months = months - back_months
#         front_monthly = remaining_budget / remaining_months if remaining_months > 0 else 0
#
#         monthly_costs = [front_monthly] * remaining_months + [back_monthly] * back_months
#
#     return monthly_costs
#
#
# # タイトル
# st.title("EC投資対効果シミュレーター")
# st.markdown("**商談中に素早く投資対効果を確認できるツール**")
#
# # 現在の日付を表示
# today = datetime.datetime.now().strftime("%Y年%m月%d日")
# st.caption(f"作成日: {today}")
#
# # --------------------------------------------
# # サイドバーの共通設定
# # --------------------------------------------
# st.sidebar.header("基本設定")
#
# # パラメータのプリセット
# preset_options = ["カスタム設定", "すぐに結果を見る（デモ値）", "食品メーカー向け", "コスメブランド向け", "アパレル向け"]
# preset_selection = st.sidebar.selectbox("設定プリセット", preset_options)
#
# # プリセット選択時の処理
# if preset_selection != "カスタム設定":
#     st.sidebar.info(f"{preset_selection}のプリセット値を使用しています。個別に値を変更することもできます。")
#
# # プリセット値の設定
# if preset_selection == "すぐに結果を見る（デモ値）":
#     default_company = "デモ株式会社"
#     default_category = "食品・飲料"
#     default_consult_fee = 300000
#     default_ad_budget = 3600000
#     default_amazon_sales = 800000
#     default_rakuten_sales = 500000
#     default_yahoo_sales = 300000
#     default_own_sales = 100000
# elif preset_selection == "食品メーカー向け":
#     default_company = ""
#     default_category = "食品・飲料"
#     default_consult_fee = 250000
#     default_ad_budget = 3000000
#     default_amazon_sales = 600000
#     default_rakuten_sales = 400000
#     default_yahoo_sales = 200000
#     default_own_sales = 50000
# elif preset_selection == "コスメブランド向け":
#     default_company = ""
#     default_category = "美容・化粧品"
#     default_consult_fee = 350000
#     default_ad_budget = 4800000
#     default_amazon_sales = 700000
#     default_rakuten_sales = 900000
#     default_yahoo_sales = 300000
#     default_own_sales = 200000
# elif preset_selection == "アパレル向け":
#     default_company = ""
#     default_category = "アパレル"
#     default_consult_fee = 300000
#     default_ad_budget = 4200000
#     default_amazon_sales = 500000
#     default_rakuten_sales = 800000
#     default_yahoo_sales = 400000
#     default_own_sales = 300000
# else:  # カスタム設定
#     default_company = ""
#     default_category = "食品・飲料"
#     default_consult_fee = 300000
#     default_ad_budget = 3600000
#     default_amazon_sales = 500000
#     default_rakuten_sales = 300000
#     default_yahoo_sales = 200000
#     default_own_sales = 100000
#
# # 企業情報入力
# st.sidebar.subheader("企業情報")
# company_name = st.sidebar.text_input("企業名", default_company)
# product_category = st.sidebar.selectbox(
#     "商品カテゴリ",
#     list(industry_defaults.keys()),
#     index=list(industry_defaults.keys()).index(default_category)
# )
#
# # 業界デフォルト値を取得
# default_growth = industry_defaults[product_category]["growth_rate"]
# default_roas = industry_defaults[product_category]["roas"]
# default_margin = industry_defaults[product_category]["profit_margin"]
#
# # シミュレーション基本設定
# st.sidebar.subheader("シミュレーション設定")
# months = st.sidebar.slider("シミュレーション期間 (月)", 3, 36, 12)
# consulting_fee = st.sidebar.number_input("コンサル費用 (円/月)", value=default_consult_fee, step=10000)
#
# # シナリオ設定
# st.sidebar.subheader("成長シナリオ")
# scenario = st.sidebar.selectbox(
#     "シナリオ選択",
#     ["保守的", "標準", "積極的"]
# )
# # シナリオごとの成長率係数
# growth_multiplier = {"保守的": 0.7, "標準": 1.0, "積極的": 1.3}
#
# # 広告予算設定
# st.sidebar.subheader("広告予算設定")
# ad_budget_total = st.sidebar.number_input("総広告予算 (円/年)", value=default_ad_budget, step=100000)
# ad_pattern = st.sidebar.selectbox(
#     "広告費配分パターン",
#     ["均等配分", "前半重点型", "段階的増加型", "後半重点型"]
# )
#
# # 商品粗利率
# profit_margin = st.sidebar.slider("商品粗利率 (%)", 10, 90, default_margin)
#
# # ヘルプ情報（折りたたみ可能）
# with st.expander("このツールの使い方"):
#     st.markdown("""
#     <div class="help-box">
#     <h4>EC投資対効果シミュレーターの使い方</h4>
#
#     <p>このツールは、EC支援サービスの導入による投資対効果を簡単にシミュレーションするためのものです。</p>
#
#     <h5>基本的な使い方</h5>
#     <ol>
#         <li>左サイドバーで基本設定を入力します（設定プリセットを選ぶとデフォルト値が設定されます）</li>
#         <li>各ECモールタブで、モール固有の設定を調整します</li>
#         <li>シミュレーション結果が自動で計算され、グラフと表で表示されます</li>
#         <li>総合レポートタブで全体の投資対効果を確認できます</li>
#     </ol>
#
#     <h5>商談で特に注目すべきポイント</h5>
#     <ul>
#         <li><strong>投資回収時期</strong>: 投資金額を回収できる月数</li>
#         <li><strong>最終月の売上</strong>: シミュレーション期間終了時の月間売上</li>
#         <li><strong>ROI</strong>: 投資対効果（投資額に対する利益の比率）</li>
#         <li><strong>オーガニック売上比率</strong>: 広告に依存しない持続的な売上の割合</li>
#     </ul>
#     </div>
#     """, unsafe_allow_html=True)
#
# # クイックレコメンデーション
# if company_name:
#     client_name = company_name
# else:
#     client_name = "お客様"
#
# # 初期表示のメッセージ（サマリー）
# if preset_selection != "カスタム設定":
#     st.info(
#         f"👋 {client_name}向けの{preset_selection}シミュレーションを実行しています。サイドバーで値を調整するか、各タブでECモール別の詳細設定を行えます。")
#
# # タブを作成（Amazon、楽天、Yahoo!ショッピング、自社EC）
# tabs = st.tabs(["Amazon", "楽天", "Yahoo!ショッピング", "自社EC", "総合レポート"])
#
# # 各モールの初期データを保存する辞書
# mall_data = {}
#
# # 各モールのシミュレーション結果
# simulation_results = {}
#
# # --------------------------------------------
# # 各モールのタブ処理
# # --------------------------------------------
# for i, mall in enumerate(["Amazon", "楽天", "Yahoo!ショッピング", "自社EC"]):
#     with tabs[i]:
#         st.subheader(f"【{mall}】シミュレーション")
#
#         # モール固有の設定を2カラムで表示
#         col1, col2 = st.columns(2)
#
#         with col1:
#             # 現状売上
#             current_sales = st.number_input(
#                 f"{mall}の現状月間売上 (円)",
#                 value=default_amazon_sales if mall == "Amazon" else default_rakuten_sales if mall == "楽天" else default_yahoo_sales if mall == "Yahoo!ショッピング" else default_own_sales,
#                 step=10000,
#                 key=f"{mall}_sales"
#             )
#
#             # 手数料率
#             fee_ratio = st.slider(
#                 f"{mall}手数料率 (%)",
#                 0, 30,
#                 mall_fee_defaults[mall],
#                 key=f"{mall}_fee"
#             )
#
#             # 広告売上比率
#             ad_sales_ratio = st.slider(
#                 "現在の広告経由売上比率 (%)",
#                 0, 100,
#                 40 if mall in ["Amazon", "楽天"] else 30,
#                 key=f"{mall}_ad_ratio"
#             )
#
#         with col2:
#             # 広告予算配分比率
#             ad_budget_ratio = st.slider(
#                 f"{mall}への広告予算配分 (%)",
#                 0, 100,
#                 40 if mall == "Amazon" else 30 if mall == "楽天" else 20 if mall == "Yahoo!ショッピング" else 10,
#                 key=f"{mall}_budget_ratio"
#             )
#
#             # 成長率設定
#             base_growth_rate = st.slider(
#                 f"{mall}の月間売上成長率 (%)",
#                 1, 50,
#                 default_growth,
#                 key=f"{mall}_growth"
#             )
#
#             # シナリオによる成長率調整
#             adjusted_growth_rate = base_growth_rate * growth_multiplier[scenario]
#             st.caption(f"{scenario}シナリオ調整後: {adjusted_growth_rate:.1f}%")
#
#             # 物流費率（Amazonと自社ECのみ）
#             if mall in ["Amazon", "自社EC"]:
#                 logistics_ratio = st.slider(
#                     "物流費率 (%)",
#                     0, 30,
#                     8 if mall == "Amazon" else 12,
#                     key=f"{mall}_logistics"
#                 )
#             else:
#                 logistics_ratio = 0
#
#         # 広告費計算
#         mall_ad_budget = ad_budget_total * (ad_budget_ratio / 100)
#         monthly_ad_costs = calculate_ad_cost_by_pattern(ad_pattern, mall_ad_budget, months)
#
#         # シミュレーション実行
#         sales_list = []
#         ad_sales_list = []
#         organic_sales_list = []
#         fee_list = []
#         logistics_costs = []
#         profit_list = []
#         roi_list = []
#
#         current_monthly_sales = current_sales
#
#         for m in range(1, months + 1):
#             # 月ごとの売上（前月比 + adjusted_growth_rate%）
#             if m == 1:
#                 monthly_sales = current_monthly_sales
#             else:
#                 monthly_sales = sales_list[-1] * (1 + adjusted_growth_rate / 100.0)
#
#             # 広告経由の売上（徐々に広告効率が改善する想定）
#             ad_efficiency_improvement = min(1 + (m - 1) * 0.05, 1.5)  # 最大で1.5倍まで改善
#             ad_sales = min(monthly_ad_costs[m - 1] * (default_roas / 100) * ad_efficiency_improvement,
#                            monthly_sales * 0.8)  # 最大でも売上の80%まで
#
#             # オーガニック売上
#             organic_sales = monthly_sales - ad_sales
#
#             # モール手数料
#             fee = monthly_sales * fee_ratio / 100.0
#
#             # 物流費
#             logistics = monthly_sales * logistics_ratio / 100.0 if logistics_ratio > 0 else 0
#
#             # 商品原価
#             cogs = monthly_sales * (100 - profit_margin) / 100.0
#
#             # 利益 = 売上 - モール手数料 - 物流費 - 商品原価 - 広告費 - コンサル費
#             monthly_profit = monthly_sales - fee - logistics - cogs - monthly_ad_costs[m - 1] - (
#                         consulting_fee / 4)  # コンサル費を4つのモールで均等に分配
#
#             # ROI計算 (投資額に対する利益の比率, %)
#             monthly_roi = (monthly_profit / (monthly_ad_costs[m - 1] + (consulting_fee / 4))) * 100 if (
#                                                                                                                    monthly_ad_costs[
#                                                                                                                        m - 1] + (
#                                                                                                                                consulting_fee / 4)) > 0 else 0
#
#             sales_list.append(monthly_sales)
#             ad_sales_list.append(ad_sales)
#             organic_sales_list.append(organic_sales)
#             fee_list.append(fee)
#             logistics_costs.append(logistics)
#             profit_list.append(monthly_profit)
#             roi_list.append(monthly_roi)
#
#         cum_profit = pd.Series(profit_list).cumsum()
#
#         # データフレーム作成
#         df_mall = pd.DataFrame({
#             "月": [f"{i}月" for i in range(1, months + 1)],
#             "売上 (円)": sales_list,
#             "広告経由売上 (円)": ad_sales_list,
#             "オーガニック売上 (円)": organic_sales_list,
#             f"{mall}手数料 (円)": fee_list,
#             "物流費 (円)": logistics_costs,
#             "広告費 (円)": monthly_ad_costs,
#             "コンサル費 (円)": [consulting_fee / 4] * months,
#             "利益 (円)": profit_list,
#             "ROI (%)": roi_list,
#             "累積利益 (円)": cum_profit
#         })
#
#         # メトリクス表示
#         st.markdown("### 📊 シミュレーション概要")
#
#         metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
#
#         with metric_col1:
#             st.metric(
#                 "初月売上",
#                 f"{int(sales_list[0]):,}円",
#                 f"{sales_list[0] - current_sales:,.0f}円"
#             )
#
#         with metric_col2:
#             st.metric(
#                 f"{months}ヶ月後売上",
#                 f"{int(sales_list[-1]):,}円",
#                 f"{(sales_list[-1] / current_sales - 1) * 100:.1f}%"
#             )
#
#         with metric_col3:
#             total_profit = sum(profit_list)
#             total_investment = sum(monthly_ad_costs) + (consulting_fee / 4) * months
#             st.metric(
#                 "総利益",
#                 f"{int(total_profit):,}円"
#             )
#
#         with metric_col4:
#             avg_roi = (total_profit / total_investment) * 100 if total_investment > 0 else 0
#             st.metric(
#                 "平均ROI",
#                 f"{avg_roi:.1f}%"
#             )
#
#         # 損益分岐点
#         break_even_point = None
#         for i, cp in enumerate(cum_profit, start=1):
#             if cp >= 0:
#                 break_even_point = i
#                 break
#
#         if break_even_point:
#             st.success(f"✅ 投資回収時期： {break_even_point}ヶ月目")
#         else:
#             st.warning("⚠️ シミュレーション期間内に投資回収に至りません。")
#
#         # 結果をシミュレーション結果辞書に保存
#         simulation_results[mall] = {
#             "sales": sales_list,
#             "ad_sales": ad_sales_list,
#             "organic_sales": organic_sales_list,
#             "profit": profit_list,
#             "cum_profit": cum_profit,
#             "total_profit": total_profit,
#             "total_investment": total_investment,
#             "roi": avg_roi,
#             "break_even": break_even_point
#         }
#
#         # グラフ表示
#         st.markdown("### 📈 シミュレーショングラフ")
#
#         # チャート選択
#         chart_type = st.radio(
#             "表示するグラフを選択",
#             ["売上推移", "累積利益", "ROI推移"],
#             horizontal=True,
#             key=f"{mall}_chart_type"
#         )
#
#         if chart_type == "売上推移":
#             # 売上推移チャート (Altair)
#             sales_data = pd.DataFrame({
#                 "月": list(range(1, months + 1)),
#                 "売上合計": sales_list,
#                 "広告経由": ad_sales_list,
#                 "オーガニック": organic_sales_list
#             })
#
#             sales_data_melted = pd.melt(
#                 sales_data,
#                 id_vars=["月"],
#                 value_vars=["広告経由", "オーガニック"],
#                 var_name="種類",
#                 value_name="売上"
#             )
#
#             sales_chart = alt.Chart(sales_data_melted).mark_bar().encode(
#                 x=alt.X("月:O", title="月"),
#                 y=alt.Y("売上:Q", title="売上 (円)"),
#                 color=alt.Color("種類:N",
#                                 scale=alt.Scale(domain=["広告経由", "オーガニック"], range=["#ff9f1c", "#2ec4b6"])),
#                 tooltip=["月", "種類", alt.Tooltip("売上:Q", format=",")]
#             ).properties(
#                 width=700,
#                 height=400,
#                 title=f"{mall}の売上推移 (広告経由 vs オーガニック)"
#             )
#
#             # 合計売上線
#             sales_line = alt.Chart(sales_data).mark_line(color="red").encode(
#                 x="月:O",
#                 y="売上合計:Q",
#                 tooltip=[alt.Tooltip("売上合計:Q", format=",")]
#             )
#
#             st.altair_chart(sales_chart + sales_line, use_container_width=True)
#
#         elif chart_type == "累積利益":
#             # 累積利益チャート (Altair)
#             profit_data = pd.DataFrame({
#                 "月": list(range(1, months + 1)),
#                 "累積利益": cum_profit
#             })
#
#             profit_chart = alt.Chart(profit_data).mark_area(
#                 color="lightgreen",
#                 line={"color": "green"}
#             ).encode(
#                 x=alt.X("月:O", title="月"),
#                 y=alt.Y("累積利益:Q", title="累積利益 (円)"),
#                 tooltip=[alt.Tooltip("月:O"), alt.Tooltip("累積利益:Q", format=",")]
#             ).properties(
#                 width=700,
#                 height=400,
#                 title=f"{mall}の累積利益推移"
#             )
#
#             # ゼロラインを追加
#             zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="red").encode(y="y")
#
#             st.altair_chart(profit_chart + zero_line, use_container_width=True)
#
#         else:  # ROI推移
#             # ROI推移チャート (Altair)
#             roi_data = pd.DataFrame({
#                 "月": list(range(1, months + 1)),
#                 "ROI": roi_list
#             })
#
#             roi_chart = alt.Chart(roi_data).mark_line(
#                 point=True
#             ).encode(
#                 x=alt.X("月:O", title="月"),
#                 y=alt.Y("ROI:Q", title="ROI (%)"),
#                 tooltip=[alt.Tooltip("月:O"), alt.Tooltip("ROI:Q", format=".1f")]
#             ).properties(
#                 width=700,
#                 height=400,
#                 title=f"{mall}のROI推移"
#             )
#
#             # ゼロラインを追加
#             zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="red").encode(y="y")
#
#             st.altair_chart(roi_chart + zero_line, use_container_width=True)
#
#         # レポート出力機能
#         st.markdown("### 📑 レポート出力")
#
#         # CSVダウンロードボタン
#         csv = df_mall.to_csv(index=False).encode('utf-8')
#         st.download_button(
#             label=f"{mall}シミュレーションデータをCSVでダウンロード",
#             data=csv,
#             file_name=f"{mall}_simulation_{today.replace('年', '').replace('月', '').replace('日', '')}.csv",
#             mime='text/csv',
#         )
#
#         # 詳細データテーブル表示（拡張可能なエクスパンダー内に配置）
#         with st.expander("詳細データを表示"):
#             st.dataframe(
#                 df_mall.style.format({
#                     "売上 (円)": "{:,.0f}",
#                     "広告経由売上 (円)": "{:,.0f}",
#                     "オーガニック売上 (円)": "{:,.0f}",
#                     f"{mall}手数料 (円)": "{:,.0f}",
#                     "物流費 (円)": "{:,.0f}",
#                     "広告費 (円)": "{:,.0f}",
#                     "コンサル費 (円)": "{:,.0f}",
#                     "利益 (円)": "{:,.0f}",
#                     "ROI (%)": "{:.1f}",
#                     "累積利益 (円)": "{:,.0f}",
#                 }),
#                 use_container_width=True,
#                 hide_index=True
#             )
#
#
#
# # --------------------------------------------
# # 総合レポートタブ
# # --------------------------------------------
# with tabs[4]:
#     if len(simulation_results) > 0:
#         st.subheader("総合シミュレーションレポート")
#
#         # 全モールの合計データを計算
#         total_sales = [sum(simulation_results[mall]["sales"][i] for mall in simulation_results) for i in range(months)]
#         total_ad_sales = [sum(simulation_results[mall]["ad_sales"][i] for mall in simulation_results) for i in
#                           range(months)]
#         total_organic_sales = [sum(simulation_results[mall]["organic_sales"][i] for mall in simulation_results) for i in
#                                range(months)]
#         total_profit = [sum(simulation_results[mall]["profit"][i] for mall in simulation_results) for i in
#                         range(months)]
#         total_cum_profit = pd.Series(total_profit).cumsum()
#
#         # 総合ROI計算
#         total_roi = sum(total_profit) / (ad_budget_total + consulting_fee * months) * 100 if (
#                                                                                                          ad_budget_total + consulting_fee * months) > 0 else 0
#
#         # 損益分岐点
#         total_break_even = None
#         for i, cp in enumerate(total_cum_profit, start=1):
#             if cp >= 0:
#                 total_break_even = i
#                 break
#
#         # メトリクス表示
#         st.markdown("### 📊 総合シミュレーション概要")
#
#         total_metric_col1, total_metric_col2, total_metric_col3, total_metric_col4 = st.columns(4)
#
#         with total_metric_col1:
#             st.metric(
#                 "初月総売上",
#                 f"{int(total_sales[0]):,}円"
#             )
#
#         with total_metric_col2:
#             current_total = sum(simulation_results[mall]["sales"][0] for mall in simulation_results)
#             final_total = sum(simulation_results[mall]["sales"][-1] for mall in simulation_results)
#
#             st.metric(
#                 f"{months}ヶ月後総売上",
#                 f"{int(final_total):,}円",
#                 f"{(final_total / current_total - 1) * 100:.1f}%"
#             )


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import datetime
import altair as alt

# ページ設定
st.set_page_config(
    page_title="EC投資対効果シミュレーター",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# カスタムCSS
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem;}
    h1 {margin-bottom: 0.5rem;}
    .stTabs [data-baseweb="tab-list"] {gap: 2rem;}
    .stTabs [data-baseweb="tab"] {height: 3rem;}
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        margin-bottom: 1rem;
    }
    /* ヘルプ情報のスタイル */
    .help-box {
        background-color: #f1f8ff;
        border-left: 5px solid #0366d6;
        padding: 1rem;
        border-radius: 0.3rem;
        margin-bottom: 1rem;
    }
    /* ボタンのスタイル強化 */
    .stButton>button {
        background-color: #0366d6;
        color: white;
        border-radius: 0.3rem;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0353b4;
    }
    /* ダウンロードボタンのスタイル */
    .stDownloadButton>button {
        background-color: #28a745;
        color: white;
    }
    .stDownloadButton>button:hover {
        background-color: #218838;
    }
</style>
""", unsafe_allow_html=True)

# 業界別のデフォルト値（成長率、ROAS※参考値, 粗利率）
industry_defaults = {
    "食品・飲料": {"growth_rate": 15, "roas_reference": 350, "profit_margin": 40}, # ROASは参考値に変更
    "美容・化粧品": {"growth_rate": 20, "roas_reference": 400, "profit_margin": 60},
    "アパレル": {"growth_rate": 18, "roas_reference": 320, "profit_margin": 45},
    "家電・デジタル": {"growth_rate": 12, "roas_reference": 280, "profit_margin": 25},
    "日用品・生活雑貨": {"growth_rate": 10, "roas_reference": 300, "profit_margin": 35},
    "その他": {"growth_rate": 15, "roas_reference": 300, "profit_margin": 40}
}


# モール別の手数料率デフォルト値
mall_fee_defaults = {
    "Amazon": 15,
    "楽天": 13,
    "Yahoo!ショッピング": 12,
    "自社EC": 5
}


# 広告費配分パターンの関数
def calculate_ad_cost_by_pattern(pattern, total_budget, months, start_ratio=0.5):
    monthly_costs = []

    if pattern == "均等配分":
        # 毎月同じ金額
        monthly_budget = total_budget / months
        monthly_costs = [monthly_budget] * months

    elif pattern == "前半重点型":
        # 前半(1-3ヶ月)に予算の60%を投入、その後減少
        front_months = min(3, months)
        front_budget = total_budget * 0.6
        front_monthly = front_budget / front_months

        remaining_budget = total_budget - front_budget
        remaining_months = months - front_months
        back_monthly = remaining_budget / remaining_months if remaining_months > 0 else 0

        monthly_costs = [front_monthly] * front_months + [back_monthly] * remaining_months

    elif pattern == "段階的増加型":
        # 徐々に予算を増やしていく
        step = 2 * total_budget / (months * (months + 1))  # 等差数列の和の公式から計算
        monthly_costs = [step * (i + 1) for i in range(months)]

    elif pattern == "後半重点型":
        # 後半に予算の60%を投入
        back_months = min(3, months)
        back_budget = total_budget * 0.6
        back_monthly = back_budget / back_months if back_months > 0 else 0

        remaining_budget = total_budget - back_budget
        remaining_months = months - back_months
        front_monthly = remaining_budget / remaining_months if remaining_months > 0 else 0

        monthly_costs = [front_monthly] * remaining_months + [back_monthly] * back_months

    return monthly_costs


# タイトル
st.title("EC投資対効果シミュレーター")
st.markdown("**商談中に素早く投資対効果を確認できるツール**")

# 現在の日付を表示
today = datetime.datetime.now().strftime("%Y年%m月%d日")
st.caption(f"作成日: {today}")

# --------------------------------------------
# サイドバーの共通設定
# --------------------------------------------
st.sidebar.header("基本設定")

# パラメータのプリセット
preset_options = ["カスタム設定", "すぐに結果を見る（デモ値）", "食品メーカー向け", "コスメブランド向け", "アパレル向け"]
preset_selection = st.sidebar.selectbox("設定プリセット", preset_options)

# プリセット選択時の処理
if preset_selection != "カスタム設定":
    st.sidebar.info(f"{preset_selection}のプリセット値を使用しています。個別に値を変更することもできます。")

# プリセット値の設定
if preset_selection == "すぐに結果を見る（デモ値）":
    default_company = "デモ株式会社"
    default_category = "食品・飲料"
    default_consult_fee = 300000
    default_ad_budget = 3600000
    default_amazon_sales = 800000
    default_rakuten_sales = 500000
    default_yahoo_sales = 300000
    default_own_sales = 100000
elif preset_selection == "食品メーカー向け":
    default_company = ""
    default_category = "食品・飲料"
    default_consult_fee = 250000
    default_ad_budget = 3000000
    default_amazon_sales = 600000
    default_rakuten_sales = 400000
    default_yahoo_sales = 200000
    default_own_sales = 50000
elif preset_selection == "コスメブランド向け":
    default_company = ""
    default_category = "美容・化粧品"
    default_consult_fee = 350000
    default_ad_budget = 4800000
    default_amazon_sales = 700000
    default_rakuten_sales = 900000
    default_yahoo_sales = 300000
    default_own_sales = 200000
elif preset_selection == "アパレル向け":
    default_company = ""
    default_category = "アパレル"
    default_consult_fee = 300000
    default_ad_budget = 4200000
    default_amazon_sales = 500000
    default_rakuten_sales = 800000
    default_yahoo_sales = 400000
    default_own_sales = 300000
else:  # カスタム設定
    default_company = ""
    default_category = "食品・飲料"
    default_consult_fee = 300000
    default_ad_budget = 3600000
    default_amazon_sales = 500000
    default_rakuten_sales = 300000
    default_yahoo_sales = 200000
    default_own_sales = 100000

# 企業情報入力
st.sidebar.subheader("企業情報")
company_name = st.sidebar.text_input("企業名", default_company)
product_category = st.sidebar.selectbox(
    "商品カテゴリ",
    list(industry_defaults.keys()),
    index=list(industry_defaults.keys()).index(default_category)
)

# 業界デフォルト値を取得 (ROASは参考値として取得)
default_growth = industry_defaults[product_category]["growth_rate"]
default_roas_ref = industry_defaults[product_category]["roas_reference"] # 参考ROAS
default_margin = industry_defaults[product_category]["profit_margin"]
st.sidebar.caption(f"参考: {product_category}の平均ROAS ≈ {default_roas_ref}%") # 参考値として表示

# シミュレーション基本設定
st.sidebar.subheader("シミュレーション設定")
months = st.sidebar.slider("シミュレーション期間 (月)", 3, 36, 12)
consulting_fee = st.sidebar.number_input("コンサル費用 (円/月)", value=default_consult_fee, step=10000)

# シナリオ設定
st.sidebar.subheader("成長シナリオ")
scenario = st.sidebar.selectbox(
    "シナリオ選択",
    ["保守的", "標準", "積極的"]
)
# シナリオごとの成長率係数
growth_multiplier = {"保守的": 0.7, "標準": 1.0, "積極的": 1.3}

# 広告予算設定
st.sidebar.subheader("広告予算設定")
ad_budget_total = st.sidebar.number_input("総広告予算 (円/年)", value=default_ad_budget, step=100000)
ad_pattern = st.sidebar.selectbox(
    "広告費配分パターン",
    ["均等配分", "前半重点型", "段階的増加型", "後半重点型"]
)

# 商品粗利率
profit_margin = st.sidebar.slider("商品粗利率 (%)", 10, 90, default_margin)

# ヘルプ情報（折りたたみ可能）
with st.expander("このツールの使い方"):
    st.markdown("""
    <div class="help-box">
    <h4>EC投資対効果シミュレーターの使い方</h4>

    <p>このツールは、EC支援サービスの導入による投資対効果を簡単にシミュレーションするためのものです。</p>

    <h5>基本的な使い方</h5>
    <ol>
        <li>左サイドバーで基本設定を入力します（設定プリセットを選ぶとデフォルト値が設定されます）</li>
        <li>各ECモールタブで、モール固有の設定を調整します</li>
        <li>シミュレーション結果が自動で計算され、グラフと表で表示されます</li>
        <li>総合レポートタブで全体の投資対効果を確認できます</li>
    </ol>

    <h5>商談で特に注目すべきポイント</h5>
    <ul>
        <li><strong>投資回収時期</strong>: 投資金額を回収できる月数</li>
        <li><strong>最終月の売上</strong>: シミュレーション期間終了時の月間売上</li>
        <li><strong>ROI</strong>: 投資対効果（投資額に対する利益の比率）</li>
        <li><strong>オーガニック売上比率</strong>: 広告に依存しない持続的な売上の割合</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# クイックレコメンデーション
if company_name:
    client_name = company_name
else:
    client_name = "お客様"

# 初期表示のメッセージ（サマリー）
if preset_selection != "カスタム設定":
    st.info(
        f"👋 {client_name}向けの{preset_selection}シミュレーションを実行しています。サイドバーで値を調整するか、各タブでECモール別の詳細設定を行えます。")

# タブを作成（Amazon、楽天、Yahoo!ショッピング、自社EC）
tabs = st.tabs(["Amazon", "楽天", "Yahoo!ショッピング", "自社EC", "総合レポート"])

# 各モールの初期データを保存する辞書
mall_data = {}

# 各モールのシミュレーション結果
simulation_results = {}

# --------------------------------------------
# 各モールのタブ処理
# --------------------------------------------
ad_budget_ratios = {}
for i, mall in enumerate(["Amazon", "楽天", "Yahoo!ショッピング", "自社EC"]):
    with tabs[i]:
        st.subheader(f"【{mall}】シミュレーション")
        col1, col2 = st.columns(2)
        with col1:
            # 現状売上 ...
            current_sales = st.number_input(
                f"{mall}の現状月間売上 (円)",
                value=default_amazon_sales if mall == "Amazon" else default_rakuten_sales if mall == "楽天" else default_yahoo_sales if mall == "Yahoo!ショッピング" else default_own_sales,
                step=10000,
                key=f"{mall}_sales"
            )
            # 手数料率 ...
            fee_ratio = st.slider(
                f"{mall}手数料率 (%)",
                0, 30,
                mall_fee_defaults[mall],
                key=f"{mall}_fee"
            )
            # *** 改良: 現状ROAS入力 ***
            current_roas = st.number_input(
                f"{mall}の現状ROAS (%)",
                min_value=1,
                value=default_roas_ref,  # デフォルトは業界参考値
                step=10,
                key=f"{mall}_roas"
            )
            # 広告売上比率 (シミュレーションでは直接使用しないが参考情報として残す場合)
            ad_sales_ratio_info = st.slider(
                "参考: 現在の広告経由売上比率 (%)",
                0, 100,
                40 if mall in ["Amazon", "楽天"] else 30,
                key=f"{mall}_ad_ratio_info",
                help="この値はシミュレーション計算には直接使用されません。現状ROASと広告予算から広告売上を計算します。"
            )
        with col2:
            # 広告予算配分比率
            ad_budget_ratio_input = st.slider( # ← この変数名を使う
                f"{mall}への広告予算配分 (%)",
                0, 100,
                40 if mall == "Amazon" else 30 if mall == "楽天" else 20 if mall == "Yahoo!ショッピング" else 10,
                key=f"{mall}_budget_ratio" # st.session_stateに保存される
            )
            ad_budget_ratios[mall] = ad_budget_ratio_input  # 後で合計チェック用
            # 成長率設定 ...
            base_growth_rate = st.slider(
                f"{mall}の月間売上成長率 (%)",
                1, 50,
                default_growth,
                key=f"{mall}_growth"
            )
            # シナリオによる成長率調整 ...
            adjusted_growth_rate = base_growth_rate * growth_multiplier[scenario]
            st.caption(f"{scenario}シナリオ調整後: {adjusted_growth_rate:.1f}%")
            # 物流費率 ...
            if mall in ["Amazon", "自社EC"]:
                logistics_ratio = st.slider(
                    "物流費率 (%)",
                    0, 30,
                    8 if mall == "Amazon" else 12,
                    key=f"{mall}_logistics"
                )
            else:
                logistics_ratio = 0
        # 広告費計算 (修正箇所)
        # mall_ad_budget = ad_budget_total * (ad_budget_ratio / 100) # ← 修正前
        mall_ad_budget = ad_budget_total * (ad_budget_ratio_input / 100) # ← 修正後: 正しい変数名を使用
        monthly_ad_costs = calculate_ad_cost_by_pattern(ad_pattern, mall_ad_budget, months)

        # シミュレーション実行
        sales_list = []
        ad_sales_list = []
        organic_sales_list = []
        fee_list = []
        logistics_costs = []
        profit_list = []
        roi_list = []
        roas_list = []  # ROASリスト初期化

        current_monthly_sales = current_sales
        initial_roas = current_roas # 入力された現状ROASを使用

        for m in range(1, months + 1):
            # 月ごとの売上（前月比 + adjusted_growth_rate%）
            if m == 1:
                monthly_sales = current_monthly_sales
            else:
                monthly_sales = sales_list[-1] * (1 + adjusted_growth_rate / 100.0)

            # 広告経由の売上（徐々に広告効率が改善する想定）
            ad_efficiency_improvement = min(1 + (m - 1) * 0.05, 1.5)
            # 広告費が0円の月は広告経由売上も0円
            if monthly_ad_costs[m - 1] > 0:
                ad_sales = min(monthly_ad_costs[m - 1] * (initial_roas / 100) * ad_efficiency_improvement,
                               monthly_sales * 0.8)  # 最大でも売上の80%まで
            else:
                 ad_sales = 0

            # オーガニック売上
            organic_sales = max(0, monthly_sales - ad_sales)  # マイナスにならないように

            # モール手数料
            fee = monthly_sales * fee_ratio / 100.0

            # 物流費
            logistics = monthly_sales * logistics_ratio / 100.0 if logistics_ratio > 0 else 0

            # 商品原価
            cogs = monthly_sales * (100 - profit_margin) / 100.0

            # 利益 = 売上 - モール手数料 - 物流費 - 商品原価 - 広告費 - コンサル費
            monthly_profit = monthly_sales - fee - logistics - cogs - monthly_ad_costs[m - 1] - (
                        consulting_fee / 4)  # コンサル費を4つのモールで均等に分配

            # ROI計算 (投資額に対する利益の比率, %)
            monthly_roi = (monthly_profit / (monthly_ad_costs[m - 1] + (consulting_fee / 4))) * 100 if (
                                                                                                                   monthly_ad_costs[
                                                                                                                       m - 1] + (
                                                                                                                               consulting_fee / 4)) > 0 else 0
            # *** ROAS計算 ***
            monthly_roas = (ad_sales / monthly_ad_costs[m - 1]) * 100 if monthly_ad_costs[m - 1] > 0 else 0

            sales_list.append(monthly_sales)
            ad_sales_list.append(ad_sales)
            organic_sales_list.append(organic_sales)
            fee_list.append(fee)
            logistics_costs.append(logistics)
            profit_list.append(monthly_profit)
            roi_list.append(monthly_roi)
            roas_list.append(monthly_roas) # ROASリストに追加


        cum_profit = pd.Series(profit_list).cumsum()
        total_ad_sales = sum(ad_sales_list) # 期間中の広告経由売上合計
        total_mall_ad_cost = sum(monthly_ad_costs) # 期間中のモール広告費合計

        # データフレーム作成 (ROAS列追加)
        df_mall = pd.DataFrame({
            "月": [f"{i}月" for i in range(1, months + 1)],
            "売上 (円)": sales_list,
            "広告経由売上 (円)": ad_sales_list,
            "オーガニック売上 (円)": organic_sales_list,
            f"{mall}手数料 (円)": fee_list,
            "物流費 (円)": logistics_costs,
            "広告費 (円)": monthly_ad_costs,
            "コンサル費 (円)": [consulting_fee / 4] * months,
            "利益 (円)": profit_list,
            "ROI (%)": roi_list,
            "ROAS (%)": roas_list,  # ← 追加
            "累積利益 (円)": cum_profit
        })

        # メトリクス表示 (5列に変更)
        st.markdown("### 📊 シミュレーション概要")
        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

        with metric_col1:
            st.metric(
                "初月売上",
                f"{int(sales_list[0]):,}円",
                f"{sales_list[0] - current_sales:,.0f}円"
            )

        with metric_col2:
            st.metric(
                f"{months}ヶ月後売上",
                f"{int(sales_list[-1]):,}円",
                f"{(sales_list[-1] / current_sales - 1) * 100:.1f}%"
            )

        with metric_col3:
            total_profit = sum(profit_list)
            total_investment = sum(monthly_ad_costs) + (consulting_fee / 4) * months
            st.metric(
                "総利益",
                f"{int(total_profit):,}円"
            )

        with metric_col4:
            # 平均ROI
            total_profit = sum(profit_list)
            total_investment = total_mall_ad_cost + (consulting_fee / 4) * months
            avg_roi = (total_profit / total_investment) * 100 if total_investment > 0 else 0
            st.metric(
                "期間平均ROI",
                f"{avg_roi:.1f}%"
                )

        with metric_col5:
             # *** 平均ROAS ***
             avg_roas = (total_ad_sales / total_mall_ad_cost) * 100 if total_mall_ad_cost > 0 else 0
             st.metric(
                 "期間平均ROAS",
                 f"{avg_roas:.1f}%",
                 help="期間中の広告経由売上 ÷ 期間中の広告費"
             )

        # 損益分岐点
        break_even_point = None
        for i, cp in enumerate(cum_profit, start=1):
            if cp >= 0:
                break_even_point = i
                break

        if break_even_point:
            st.success(f"✅ 投資回収時期： {break_even_point}ヶ月目")
        else:
            st.warning("⚠️ シミュレーション期間内に投資回収に至りません。")

            # *** simulation_results に必要な情報を追加 ***
            simulation_results[mall] = {
                "sales": sales_list,
                "ad_sales": ad_sales_list,
                "organic_sales": organic_sales_list,
                "profit": profit_list,
                "cum_profit": cum_profit,
                "total_profit": total_profit,
                "total_investment": total_investment,  # モール単位の投資額(広告費+按分コンサル費)
                "roi": avg_roi,
                "roas": avg_roas,  # モール単位の平均ROAS
                "break_even": break_even_point,
                "monthly_ad_costs": monthly_ad_costs,  # 月次広告費リスト追加
                "total_ad_sales": total_ad_sales,  # 期間広告売上合計追加
                "total_mall_ad_cost": total_mall_ad_cost  # 期間モール広告費合計追加
            }

        # グラフ表示
        st.markdown("### 📈 シミュレーショングラフ")
        # チャート選択 (ROAS推移追加)
        chart_type = st.radio(
            "表示するグラフを選択",
            ["売上推移", "累積利益", "ROI推移", "ROAS推移"], # ← ROAS推移追加
            horizontal=True,
            key=f"{mall}_chart_type"
        )



        if chart_type == "売上推移":
            # 売上推移チャート (Altair)
            sales_data = pd.DataFrame({
                "月": list(range(1, months + 1)),
                "売上合計": sales_list,
                "広告経由": ad_sales_list,
                "オーガニック": organic_sales_list
            })

            sales_data_melted = pd.melt(
                sales_data,
                id_vars=["月"],
                value_vars=["広告経由", "オーガニック"],
                var_name="種類",
                value_name="売上"
            )

            sales_chart = alt.Chart(sales_data_melted).mark_bar().encode(
                x=alt.X("月:O", title="月"),
                y=alt.Y("売上:Q", title="売上 (円)"),
                color=alt.Color("種類:N",
                                scale=alt.Scale(domain=["広告経由", "オーガニック"], range=["#ff9f1c", "#2ec4b6"])),
                tooltip=["月", "種類", alt.Tooltip("売上:Q", format=",")]
            ).properties(
                width=700,
                height=400,
                title=f"{mall}の売上推移 (広告経由 vs オーガニック)"
            )

            # 合計売上線
            sales_line = alt.Chart(sales_data).mark_line(color="red").encode(
                x="月:O",
                y="売上合計:Q",
                tooltip=[alt.Tooltip("売上合計:Q", format=",")]
            )

            st.altair_chart(sales_chart + sales_line, use_container_width=True)

        elif chart_type == "累積利益":
            # 累積利益チャート (Altair)
            profit_data = pd.DataFrame({
                "月": list(range(1, months + 1)),
                "累積利益": cum_profit
            })

            profit_chart = alt.Chart(profit_data).mark_area(
                color="lightgreen",
                line={"color": "green"}
            ).encode(
                x=alt.X("月:O", title="月"),
                y=alt.Y("累積利益:Q", title="累積利益 (円)"),
                tooltip=[alt.Tooltip("月:O"), alt.Tooltip("累積利益:Q", format=",")]
            ).properties(
                width=700,
                height=400,
                title=f"{mall}の累積利益推移"
            )

            # ゼロラインを追加
            zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="red").encode(y="y")

            st.altair_chart(profit_chart + zero_line, use_container_width=True)
        elif chart_type == "ROI推移":
            # ROI推移チャート (Altair)
            roi_data = pd.DataFrame({
                "月": list(range(1, months + 1)),
                "ROI": roi_list
            })
            roi_chart = alt.Chart(roi_data).mark_line(
                point=True,
                color="blue"  # 色指定の例
            ).encode(
                x=alt.X("月:O", title="月"),
                y=alt.Y("ROI:Q", title="ROI (%)"),
                tooltip=[alt.Tooltip("月:O"), alt.Tooltip("ROI:Q", format=".1f")]
            ).properties(
                width=700,
                height=400,
                title=f"{mall}のROI推移"
            )
            zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="red").encode(y="y")
            st.altair_chart(roi_chart + zero_line, use_container_width=True)

        elif chart_type == "ROAS推移":  # ← ROASグラフ描画追加
            roas_data = pd.DataFrame({
                "月": list(range(1, months + 1)),
                "ROAS": roas_list
            })
            roas_chart = alt.Chart(roas_data).mark_line(
                point=True,
                color="orange"  # 色指定の例
            ).encode(
                x=alt.X("月:O", title="月"),
                y=alt.Y("ROAS:Q", title="ROAS (%)"),
                tooltip=[alt.Tooltip("月:O"), alt.Tooltip("ROAS:Q", format=".1f")]
            ).properties(
                width=700,
                height=400,
                title=f"{mall}のROAS推移"
            )
            st.altair_chart(roas_chart, use_container_width=True)

        # レポート出力機能
        st.markdown("### 📑 レポート出力")
        # CSVダウンロードボタン ...
        # 詳細データテーブル表示 (ROASフォーマット追加)
        with st.expander("詳細データを表示"):
            st.dataframe(
                df_mall.style.format({
                    # ... (既存フォーマット)
                    "利益 (円)": "{:,.0f}",
                    "ROI (%)": "{:.1f}",
                    "ROAS (%)": "{:.1f}",  # ← 追加
                    "累積利益 (円)": "{:,.0f}",
                }),
                use_container_width=True,
                hide_index=True
            )

        # CSVダウンロードボタン
        csv = df_mall.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"{mall}シミュレーションデータをCSVでダウンロード",
            data=csv,
            file_name=f"{mall}_simulation_{today.replace('年', '').replace('月', '').replace('日', '')}.csv",
            mime='text/csv',
        )

        # 詳細データテーブル表示（拡張可能なエクスパンダー内に配置）
        with st.expander("詳細データを表示"):
            st.dataframe(
                df_mall.style.format({
                    "売上 (円)": "{:,.0f}",
                    "広告経由売上 (円)": "{:,.0f}",
                    "オーガニック売上 (円)": "{:,.0f}",
                    f"{mall}手数料 (円)": "{:,.0f}",
                    "物流費 (円)": "{:,.0f}",
                    "広告費 (円)": "{:,.0f}",
                    "コンサル費 (円)": "{:,.0f}",
                    "利益 (円)": "{:,.0f}",
                    "ROI (%)": "{:.1f}",
                    "累積利益 (円)": "{:,.0f}",
                }),
                use_container_width=True,
                hide_index=True
            )



# --------------------------------------------
# 総合レポートタブ
# --------------------------------------------
with tabs[4]:
    if not simulation_results:
         st.warning("各モールの設定を入力してシミュレーションを実行してください。")
    else:
        st.subheader("総合シミュレーションレポート")

        # *** 改良: 広告予算配分比率の合計チェック ***
        total_ratio = sum(st.session_state.get(f"{mall}_budget_ratio", 0) for mall in ["Amazon", "楽天", "Yahoo!ショッピング", "自社EC"])
        if not np.isclose(total_ratio, 100) and total_ratio > 0: # 0の場合はまだ入力中とみなす
            st.warning(f"注意: 各モールへの広告予算配分比率の合計が {total_ratio:.1f}% です。100%になるように調整してください。", icon="⚠️")

        # 全モールの合計データを計算
        # ... (total_sales, total_ad_sales, total_organic_sales, total_profit, total_cum_profit 計算)
        # total_profitリストを先に計算
        total_profit_list = [sum(simulation_results[mall]["profit"][i] for mall in simulation_results) for i in range(months)]
        total_cum_profit = pd.Series(total_profit_list).cumsum()

        # 総合ROI計算
        overall_total_profit = sum(total_profit_list)
        overall_total_investment = ad_budget_total + consulting_fee * months
        total_roi = (overall_total_profit / overall_total_investment) * 100 if overall_total_investment > 0 else 0

        # *** 総合平均ROAS計算 ***
        overall_total_ad_sales = sum(simulation_results[mall]["total_ad_sales"] for mall in simulation_results)
        # total_ad_cost_all = ad_budget_total # 年間予算を使う場合
        # 月次実績ベースの合計を使う場合
        overall_total_ad_cost = sum(simulation_results[mall]["total_mall_ad_cost"] for mall in simulation_results)
        overall_avg_roas = (overall_total_ad_sales / overall_total_ad_cost) * 100 if overall_total_ad_cost > 0 else 0

        # 損益分岐点
        total_break_even = None
        for i, cp in enumerate(total_cum_profit, start=1):
            if cp >= 0:
                total_break_even = i
                break

        # メトリクス表示
        st.markdown("### 📊 総合シミュレーション概要")
        total_metric_col1, total_metric_col2, total_metric_col3, total_metric_col4, total_metric_col5 = st.columns(5)

        with total_metric_col1:
            # 初月総売上
            total_sales_list = [sum(simulation_results[mall]["sales"][i] for mall in simulation_results) for i in
                                range(months)]
            st.metric(
                "初月総売上",
                f"{int(total_sales_list[0]):,}円"
            )


        with total_metric_col2:
             # Xヶ月後総売上
             # current_total = sum(simulation_results[mall]["sales"][0] for mall in simulation_results) # 初月売上は total_sales_list[0] でOK
             final_total = total_sales_list[-1]
             growth_pct = (final_total / total_sales_list[0] - 1) * 100 if total_sales_list[0] > 0 else 0
             st.metric(
                 f"{months}ヶ月後総売上",
                 f"{int(final_total):,}円",
                 f"{growth_pct:.1f}%"
             )

        with total_metric_col3:
            # 期間総利益
            st.metric(
                "期間総利益",
                f"{int(overall_total_profit):,}円"
            )

        with total_metric_col4:
            # 総合ROI
            st.metric(
                "総合ROI",
                f"{total_roi:.1f}%",
                help="期間総利益 ÷ (総広告予算 + 総コンサル費用)"
            )

        with total_metric_col5:
            # *** 総合平均ROAS ***
            st.metric(
                "総合平均ROAS",
                f"{overall_avg_roas:.1f}%",
                help="期間中の全モール広告経由売上 ÷ 期間中の全モール広告費"
            )

        # 損益分岐点表示
        if total_break_even:
            st.success(f"✅ 全体の投資回収時期： {total_break_even}ヶ月目 (累積利益がプラスになる月)")
        else:
            st.warning("⚠️ シミュレーション期間内に全体の投資回収に至りません。")

        # --- 総合グラフ表示 (オプションとして追加可能) ---
        st.markdown("### 📈 総合グラフ")
        overall_chart_type = st.selectbox(
            "表示する総合グラフを選択",
            ["総売上推移", "累積利益推移", "総利益推移(月次)"]
        )

        # 総合データフレーム作成
        df_overall = pd.DataFrame({
            "月": list(range(1, months + 1)),
            "総売上": total_sales_list,
            "総利益": total_profit_list,
            "累積総利益": total_cum_profit
        })

        if overall_chart_type == "総売上推移":
            overall_sales_chart = alt.Chart(df_overall).mark_line(point=True).encode(
                x=alt.X("月:O"),
                y=alt.Y("総売上:Q", title="総売上 (円)"),
                tooltip=[alt.Tooltip("月:O"), alt.Tooltip("総売上:Q", format=",")]
            ).properties(title="全モールの総売上推移")
            st.altair_chart(overall_sales_chart, use_container_width=True)

        elif overall_chart_type == "累積利益推移":
            overall_profit_chart = alt.Chart(df_overall).mark_area(
                color="lightgreen",
                line={"color": "green"}
            ).encode(
                x=alt.X("月:O"),
                y=alt.Y("累積総利益:Q", title="累積総利益 (円)"),
                tooltip=[alt.Tooltip("月:O"), alt.Tooltip("累積総利益:Q", format=",")]
            ).properties(title="全モールの累積利益推移")
            zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="red").encode(y="y")
            st.altair_chart(overall_profit_chart + zero_line, use_container_width=True)

        elif overall_chart_type == "総利益推移(月次)":
            overall_monthly_profit_chart = alt.Chart(df_overall).mark_bar().encode(
                x=alt.X("月:O"),
                y=alt.Y("総利益:Q", title="月次総利益 (円)"),
                tooltip=[alt.Tooltip("月:O"), alt.Tooltip("総利益:Q", format=",")],
                color=alt.condition(
                    alt.datum.総利益 > 0,
                    alt.value("steelblue"),  # 黒字は青系
                    alt.value("coral")  # 赤字は赤系
                )
            ).properties(title="全モールの月次利益推移")
            st.altair_chart(overall_monthly_profit_chart, use_container_width=True)

        # --- モール別貢献度 (パイチャート例) ---
        st.markdown("### 📊 モール別貢献度 (期間全体)")
        contrib_col1, contrib_col2 = st.columns(2)

        with contrib_col1:
            st.write("**売上構成比**")
            sales_composition = {mall: sum(simulation_results[mall]["sales"]) for mall in simulation_results}
            df_sales_comp = pd.DataFrame(list(sales_composition.items()), columns=['モール', '売上']).sort_values(
                '売上', ascending=False)
            if df_sales_comp['売上'].sum() > 0:
                sales_pie = alt.Chart(df_sales_comp).mark_arc(outerRadius=120).encode(
                    theta=alt.Theta(field="売上", type="quantitative", stack=True),
                    color=alt.Color(field="モール", type="nominal"),
                    tooltip=['モール', alt.Tooltip('売上', format=',.0f', title='期間合計売上')]
                ).properties(title='モール別 売上構成比')
                st.altair_chart(sales_pie, use_container_width=True)
            else:
                st.info("売上データがありません。")

        with contrib_col2:
            st.write("**利益構成比**")
            profit_composition = {mall: simulation_results[mall]["total_profit"] for mall in simulation_results}
            # マイナス利益を除外するか、そのまま表示するか検討 (ここではそのまま表示)
            df_profit_comp = pd.DataFrame(list(profit_composition.items()), columns=['モール', '利益']).sort_values(
                '利益', ascending=False)
            # 利益が0以下のモールを除外してパイチャートを作成する場合
            # df_profit_comp_positive = df_profit_comp[df_profit_comp['利益'] > 0]
            # if not df_profit_comp_positive.empty:
            if df_profit_comp['利益'].sum() != 0 or not df_profit_comp.empty:  # 合計が0でないか、空でない場合
                profit_pie = alt.Chart(df_profit_comp).mark_arc(outerRadius=120).encode(
                    # マイナス値を考慮する場合、thetaでのstackは注意が必要。絶対値で割合を見るなどの工夫も可
                    theta=alt.Theta(field="利益", type="quantitative", stack=True),  # マイナスがあると表示が崩れる可能性あり
                    color=alt.Color(field="モール", type="nominal"),
                    tooltip=['モール', alt.Tooltip('利益', format=',.0f', title='期間合計利益')]
                ).properties(title='モール別 利益構成比')
                st.altair_chart(profit_pie, use_container_width=True)
            else:
                st.info("利益データがありません（または全て0以下）。")

        # --- 総合詳細データ (オプション) ---
        # 全モールのデータを結合した詳細データフレームを表示することも可能
        # with st.expander("全モールの月次詳細データ（結合）"):
        #     # 各df_mallを結合する処理...
        #     st.dataframe(...)
