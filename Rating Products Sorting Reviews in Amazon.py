import matplotlib.pyplot as plt
import pandas as pd
import math
import scipy.stats as st

pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', 10)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


df = pd.read_csv("amazon_review.csv")
#ürünün ortalama puanı
df["overall"].mean()


#tarihe göre ağırlıklı puan hesaplaması

df['reviewTime'] = pd.to_datetime(df['reviewTime'], dayfirst=True)
df.info()
current_date = pd.to_datetime(str(df['reviewTime'].max()))

df["day_diff"] = (current_date - df['reviewTime']).dt.days

def time_based_weighted_average(dataframe, w1=24, w2=22, w3=20, w4=18, w5=16):
    return dataframe.loc[dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.2), "overall"].mean() * w1 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.2)) & (dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.4)), "overall"].mean() * w2 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.4)) & (dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.6)), "overall"].mean() * w3 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.6)) & (dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.8)), "overall"].mean() * w4 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.8)), "overall"].mean() * w5 / 100

time_based_weighted_average(df)

#yararlı bulunmayan yorum sayısı


df["helpful_no"] = df["total_vote"] - df["helpful_yes"]

df = df[["reviewerName", "overall", "summary", "helpful_yes", "helpful_no", "total_vote", "reviewTime"]]
df.head()


#score_pos_neg_diff, score_average_rating ve wilson_lower_bound skorlarını hesaplayıp veriye ekleyiniz.

def wilson_lower_bound(up, down, confidence=0.95):
    """
    Wilson Lower Bound Score hesapla

    - Bernoulli parametresi p için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    - Hesaplanacak skor ürün sıralaması için kullanılır.
    - Not:
    Eğer skorlar 1-5 arasıdaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulli'ye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

    Parameters
    ----------
    up: int
        up count
    down: int
        down count
    confidence: float
        confidence

    Returns
    -------
    wilson score: float

    """
    n = up + down
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

def score_up_down_diff(up, down):
    return up - down

def score_average_rating(up, down):
    if up + down == 0:
        return 0
    return up / (up + down)

# score_pos_neg_diff
df["score_pos_neg_diff"] = df.apply(lambda x: score_up_down_diff(x["helpful_yes"], x["helpful_no"]), axis=1)

# score_average_rating
df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)

# wilson_lower_bound
df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)

#wilson lower bound'a göre ilk 20 yorumun belirlenmesi
df.sort_values("wilson_lower_bound", ascending=False).head(20)
