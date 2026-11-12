# So output dạng chữ của hai bản notebook đã chạy

- A: `/home/user/scratch/ev/orig/executed/06_predict_aqi.ipynb`
- B: `/home/user/scratch/ev/chains/nb06_only/executed/06_predict_aqi.ipynb`

Tổng: 26 ô mã chung, 21 ô có output dạng chữ khác, 236 dòng khác, 267 số khác (trên các dòng ghép được), lệch số lớn nhất 1946.99.

| Ô (A) | Ô (B) | id | dòng khác | số khác | lệch số lớn nhất | hình A | hình B |
|---|---|---|---|---|---|---|---|
| 3 | 3 | `60ee5880` | 5 | 2 | 5 | 0 | 0 |
| 5 | 5 | `23317e4a` | 47 | 8 | 5 | 0 | 0 |
| 6 | 6 | `4b6742a3` | 26 | 0 | 0 | 0 | 0 |
| 9 | 9 | `f1d19bbb` | 4 | 15 | 4 | 0 | 0 |
| 10 | 10 | `284a1f9e` | 10 | 20 | 100 | 0 | 0 |
| 13 | 13 | `418fa316` | 5 | 13 | 11.59 | 0 | 0 |
| 15 | 15 | `023e10d4` | 0 | 0 | 0 | 1 | 1 |
| 18 | 18 | `4bd5bbdc` | 36 | 51 | 0.2 | 0 | 0 |
| 21 | 21 | `5c24a416` | 9 | 43 | 2.06 | 0 | 0 |
| 22 | 22 | `7ff1c676` | 6 | 16 | 0.12 | 0 | 0 |
| 24 | 24 | `36afa4a5` | 0 | 0 | 0 | 1 | 1 |
| 27 | 27 | `098bb393` | 7 | 7 | 0.1 | 1 | 1 |
| 30 | 30 | `35e0efd4` | 2 | 5 | 4 | 0 | 0 |
| 32 | 32 | `e2c7378e` | 5 | 36 | 9 | 0 | 0 |
| 34 | 34 | `acd9840b` | 9 | 27 | 0.011 | 0 | 0 |
| 37 | 37 | `f2ab0f4f` | 0 | 0 | 0 | 1 | 1 |
| 40 | 40 | `1a783eb9` | 1 | 1 | 0.03 | 0 | 0 |
| 43 | 43 | `c30ab3a0` | 0 | 0 | 0 | 0 | 0 |
| 45 | 45 | `ca8502bb` | 0 | 0 | 0 | 1 | 1 |
| 48 | 48 | `fc0d5ea2` | 1 | 1 | 0.1 | 0 | 0 |
| 51 | 51 | `2073a84f` | 3 | 5 | 0.04 | 0 | 0 |
| 52 | 52 | `da84d4dc` | 2 | 6 | 0.03 | 0 | 0 |
| 53 | 53 | `5bad2128` | 54 | 3 | 1946.99 | 0 | 0 |
| 54 | 54 | `296ab635` | 2 | 2 | 0.02 | 0 | 0 |
| 55 | 55 | `09edbe64` | 1 | 6 | 0.02 | 0 | 0 |
| 58 | 58 | `e084a76b` | 1 | 0 | 0 | 0 | 0 |

- Ô mã chỉ có ở A: không; chỉ có ở B: ['r2f01sum1']

## Ô 3 (A) / 3 (B), id `60ee5880`: 5 dòng khác, 2 số khác, lệch số lớn nhất 5

- A: `train     5741       1432 2017-06-15 2019-06-30`
+ B: `train     5746       1436 2017-06-15 2019-06-30`
+ B: `  raw: sha256 0d84b21c3e4878bb | snapshot 0d84b21c3e4878bb | TRÙNG`
+ B: `  thời tiết theo ngày: sha256 45f3579a222c55c0 | snapshot 45f3579a222c55c0 | TRÙNG`
+ B: `  bảng sạch hồi cứu (chỉ để đối chiếu): sha256 38653221fda73fed | snapshot 38653221fda73fed | TRÙNG`
+ B: `  => mọi đầu vào đúng snapshot: mọi con số thực nghiệm phải khớp.`

## Ô 5 (A) / 5 (B), id `23317e4a`: 47 dòng khác, 8 số khác, lệch số lớn nhất 5

- A: `Gurugram        685               390      244               97            123                      2`
+ B: `Gurugram        687               392      244               97            123                      2`

- A: `Jaipur          716               111      244                9            123                      0`
- A: `Bengaluru       737                 2      244                0            123                      0`
+ B: `Jaipur          718               113      244                9            123                      0`
+ B: `Bengaluru       738                 2      244                0            123                      0`

- A: `Cộng           5741              1432     1947              389            975                     18`
- A: `Tỉ lệ ngày AQI >= 201: train 24.9%, test 20.0%, 03-07/2020 1.8%`
+ B: `Cộng           5746              1436     1947              389            975                     18`
+ B: `Tỉ lệ ngày AQI >= 201: train 25.0%, test 20.0%, 03-07/2020 1.8%`
+ B: ``
+ B: `Bảng giữ mẫu (mẫu được giữ khi raw có AQI ở CẢ ngày t và ngày lịch t+1):`
+ B: `          cặp (thành phố, ngày t) trong khoảng  thiếu AQI(t)  có AQI(t), thiếu AQI(t+1)  giữ (có cả hai)  ngày nặng trong số giữ`
+ B: `split`
+ B: `train                                     5968           164                         58             5746                    1436`
+ B: `test                                      1952             3                          2             1947                     389`
+ B: `lockdown                                   984             7                          2              975                      18`
+ B: `Cộng                                      8904           174                         62             8668                    1843`
+ B: ``
+ B: `So với đường hồi cứu cũ (8,663 mẫu): đường dự báo từ raw có 8,668 mẫu; 5 mẫu chỉ có ở đường mới, 0 mẫu chỉ có ở đường cũ.`
+ B: `                        cohort       City        Date Date_target  split  AQI_raw(t)  AQI_raw(t+1)  AQI_sach(t)  AQI_sach(t+1)  y_poor  \`
+ B: `0  chỉ có ở đường dự báo (raw)  Bengaluru  2017-07-08  2017-07-09  train       108.0         112.0          NaN          112.0   False`
+ B: `1  chỉ có ở đường dự báo (raw)   Gurugram  2017-07-08  2017-07-09  train       372.0         529.0        372.0            NaN    True`
+ B: `2  chỉ có ở đường dự báo (raw)   Gurugram  2017-07-29  2017-07-30  train       248.0         482.0        248.0            NaN    True`
+ B: `3  chỉ có ở đường dự báo (raw)     Jaipur  2018-02-05  2018-02-06  train       153.0         305.0        153.0            NaN    True`
+ B: `4  chỉ có ở đường dự báo (raw)     Jaipur  2018-02-06  2018-02-07  train       305.0         291.0          NaN          291.0    True`
+ B: ``
+ B: `                                                             nguyen_nhan`
+ B: `0              bảng sạch hồi cứu đã xoá AQI(t) (cờ suspect_sensor_error)`
+ B: `1  bảng sạch hồi cứu đã xoá AQI(t+1), tức nhãn (cờ suspect_sensor_error)`
+ B: `2  bảng sạch hồi cứu đã xoá AQI(t+1), tức nhãn (cờ suspect_sensor_error)`
+ B: `3  bảng sạch hồi cứu đã xoá AQI(t+1), tức nhãn (cờ suspect_sensor_error)`
+ B: `4              bảng sạch hồi cứu đã xoá AQI(t) (cờ suspect_sensor_error)`
+ B: ``
+ B: `Quy tắc số 0 treo (tính đến ngày t đã có >= 3 ngày 0 liên tiếp) chỉ áp cho ['PM2.5', 'NO2', 'CO', 'SO2', 'O3']; điền bằng giá trị của tối đa 2 ngày trước. Từng ô bị che: 252 ô (lưu ở nb06_masked_cells.csv).`
+ B: `                            số mẫu  che số 0 treo tại t  giá trị dùng là số 0  dùng giá trị ngày t  điền từ t-1  điền từ t-2  không có nguồn (imputer của train)`
+ B: `đặc trưng cột raw tập`
+ B: `pm25_0    PM2.5   train       5746                    0                     0                 5656            6            5                                  79`
+ B: `                  test        1947                    0                     0                 1947            0            0                                   0`
+ B: `                  lockdown     975                    0                     0                  975            0            0                                   0`
+ B: `no2_0     NO2     train       5746                    0                     0                 5736            5            1                                   4`
+ B: `                  test        1947                    0                     0                 1947            0            0                                   0`
+ B: `                  lockdown     975                    0                     0                  975            0            0                                   0`
+ B: `co_0      CO      train       5746                  252                    81                 5461            6            4                                 275`
+ B: `                  test        1947                    0                     0                 1947            0            0                                   0`
+ B: `                  lockdown     975                    0                     0                  975            0            0                                   0`
+ B: `so2_0     SO2     train       5746                    0                     0                 5446           31           18                                 251`
+ B: `                  test        1947                    0                     0                 1946            1            0                                   0`
+ B: `                  lockdown     975                    0                     0                  975            0            0                                   0`
+ B: `o3_0      O3      train       5746                    0                     0                 5585           11            6                                 144`
+ B: `                  test        1947                    0                     0                 1929            3            3                                  12`
+ B: `                  lockdown     975                    0                     0                  972            1            1                                   1`

## Ô 6 (A) / 6 (B), id `4b6742a3`: 26 dòng khác, 0 số khác, lệch số lớn nhất 0

- A: `Đạt cả 3 kiểm tra: đặc trưng của ngày t không dùng dữ liệu sau t.`
+ B: `            số thành phố  ô khác (cắt raw ở t)  ô khác (nhiễu dữ liệu sau t) dòng muộn nhất trong bản cắt`
+ B: `ngày cắt t`
+ B: `2017-06-14             8                     0                             0                   2017-06-14`
+ B: `2017-07-08             8                     0                             0                   2017-07-08`
+ B: `2017-07-09             8                     0                             0                   2017-07-09`
+ B: `2017-07-30             8                     0                             0                   2017-07-30`
+ B: `2017-08-12             8                     0                             0                   2017-08-12`
+ B: `2017-08-29             8                     0                             0                   2017-08-29`
+ B: `2017-08-30             8                     0                             0                   2017-08-30`
+ B: `2017-11-09             8                     0                             0                   2017-11-09`
+ B: `2017-11-13             8                     0                             0                   2017-11-13`
+ B: `2018-02-06             8                     0                             0                   2018-02-06`
+ B: `2018-06-15             8                     0                             0                   2018-06-15`
+ B: `2018-09-15             8                     0                             0                   2018-09-15`
+ B: `2017-07-14             8                     0                             0                   2017-07-14`
+ B: `2017-07-16             8                     0                             0                   2017-07-16`
+ B: `2018-05-01             8                     0                             0                   2018-05-01`
+ B: `2018-12-01             8                     0                             0                   2018-12-01`
+ B: `2019-11-15             8                     0                             0                   2019-11-15`
+ B: `2020-01-10             8                     0                             0                   2020-01-10`
+ B: `2019-06-29             8                     0                             0                   2019-06-29`
+ B: `2019-06-30             8                     0                             0                   2019-06-30`
+ B: `2020-02-28             8                     0                             0                   2020-02-28`
+ B: `2020-02-29             8                     0                             0                   2020-02-29`
+ B: `2020-06-30             8                     0                             0                   2020-06-30`
+ B: `Đạt cả 5 kiểm tra: tại 23 ngày thử, đặc trưng của ngày t không đổi một ô nào khi cắt raw ở t hoặc làm nhiễu dữ liệu sau t.`

## Ô 9 (A) / 9 (B), id `f1d19bbb`: 4 dòng khác, 15 số khác, lệch số lớn nhất 4

- A: `1                       18/11/2017  20/11/2017 - 19/04/2018   1133          1148                     432`
- A: `2                       17/04/2018  19/04/2018 - 14/09/2018   2281          1148                     147`
- A: `3                       12/09/2018  15/09/2018 - 06/02/2019   3429          1148                     405`
- A: `4                       04/02/2019  07/02/2019 - 30/06/2019   4577          1148                     209`
+ B: `1                       18/11/2017  20/11/2017 - 19/04/2018   1134          1149                     434`
+ B: `2                       16/04/2018  19/04/2018 - 14/09/2018   2283          1149                     148`
+ B: `3                       12/09/2018  14/09/2018 - 06/02/2019   3432          1149                     404`
+ B: `4                       04/02/2019  06/02/2019 - 30/06/2019   4581          1149                     210`

## Ô 10 (A) / 10 (B), id `284a1f9e`: 10 dòng khác, 20 số khác, lệch số lớn nhất 100

- A: `Trung bình theo thành phố                                            60.49                10.42                 —`
- A: `Trung vị cùng tháng (khí hậu)                                        55.82                15.75                 —`
- A: `Ngày mai = hôm nay                                                   25.93                 1.27                 —`
- A: `Ridge L1: Mức 1: chỉ AQI các ngày trước                              25.52                 1.41        alpha = 10`
- A: `Ridge L2: Mức 2: + chất ô nhiễm hôm nay                              23.73                 1.50       alpha = 0.1`
- A: `Ridge L3: Mức 3: + thời tiết đến hôm nay                             22.33                 1.16        alpha = 30`
- A: `Ridge L4: Cận trên: + thời tiết ngày mai (dự báo hoàn hảo)           22.16                 1.21        alpha = 10`
- A: `Cây tăng cường (HGB) L1                                              26.13                 1.39  depth 2, 100 cây`
- A: `Cây tăng cường (HGB) L2                                              22.84                 1.03  depth 2, 200 cây`
- A: `Cây tăng cường (HGB) L3                                              22.28                 1.35  depth 2, 200 cây`
+ B: `Trung bình theo thành phố                                            60.54                10.36                 —`
+ B: `Trung vị cùng tháng (khí hậu)                                        56.12                15.58                 —`
+ B: `Ngày mai = hôm nay                                                   25.96                 1.22                 —`
+ B: `Ridge L1: Mức 1: chỉ AQI các ngày trước                              25.52                 1.38        alpha = 10`
+ B: `Ridge L2: Mức 2: + chất ô nhiễm hôm nay                              23.72                 1.41       alpha = 0.1`
+ B: `Ridge L3: Mức 3: + thời tiết đến hôm nay                             22.34                 1.11        alpha = 30`
+ B: `Ridge L4: Cận trên: + thời tiết ngày mai (dự báo hoàn hảo)           22.21                 1.17        alpha = 10`
+ B: `Cây tăng cường (HGB) L1                                              26.20                 1.35  depth 2, 200 cây`
+ B: `Cây tăng cường (HGB) L2                                              22.94                 1.12  depth 2, 200 cây`
+ B: `Cây tăng cường (HGB) L3                                              22.43                 1.50  depth 2, 200 cây`

## Ô 13 (A) / 13 (B), id `418fa316`: 5 dòng khác, 13 số khác, lệch số lớn nhất 11.59

- A: `Dòng đủ đặc trưng: 5118/5741 (89%) · R² hiệu chỉnh trong mẫu (log AQI): 0.891 (KHÔNG phải thước đo chất lượng, xem Phần E)`
+ B: `Dòng đủ đặc trưng: 5125/5746 (89%) · R² hiệu chỉnh trong mẫu (log AQI): 0.890 (KHÔNG phải thước đo chất lượng, xem Phần E)`

- A: `Breusch-Pagan LM                           408.51              311.11`
+ B: `Breusch-Pagan LM                           420.10              316.05`

- A: `ACF lag 1   0.07      0.15     0.05     0.0       0.02      0.07     0.12       0.34`
+ B: `ACF lag 1   0.07      0.19     0.05    0.01       0.02      0.07     0.12       0.34`

- A: `VIF   14.5   12.2    10.9    9.9        8.8     8.3      7.4       6.2`
- A: `Cook's distance: 343 dòng vượt 4/n (6.7%), lớn nhất 0.078`
+ B: `VIF   14.5   12.1    10.8    9.8        8.7     8.3      7.4       6.2`
+ B: `Cook's distance: 345 dòng vượt 4/n (6.7%), lớn nhất 0.077`

## Ô 18 (A) / 18 (B), id `4bd5bbdc`: 36 dòng khác, 51 số khác, lệch số lớn nhất 0.2

- A: `aqi_0            0.376     0.000`
- A: `aqi_1           -0.073     0.000`
- A: `aqi_2            0.049     0.015`
+ B: `aqi_0            0.375     0.000`
+ B: `aqi_1           -0.070     0.000`
+ B: `aqi_2            0.047     0.017`

- A: `pm25_0           0.305     0.000`
- A: `no2_0            0.019     0.062`
- A: `co_0             0.047     0.015`
- A: `so2_0            0.001     0.912`
- A: `o3_0             0.034     0.000`
- A: `temp_mean       -0.000     0.960`
- A: `humidity_mean   -0.001     0.011`
- A: `pressure_dev    -0.003     0.304`
- A: `d_pressure      -0.006     0.178`
+ B: `pm25_0           0.306     0.000`
+ B: `no2_0            0.019     0.067`
+ B: `co_0             0.046     0.015`
+ B: `so2_0            0.000     0.985`
+ B: `o3_0             0.035     0.000`
+ B: `temp_mean       -0.000     0.964`
+ B: `humidity_mean   -0.001     0.015`
+ B: `pressure_dev    -0.003     0.336`
+ B: `d_pressure      -0.006     0.172`

- A: `wind_v          -0.005     0.092`
- A: `blh_mean         0.000     0.768`
+ B: `wind_v          -0.005     0.088`
+ B: `blh_mean         0.000     0.782`

- A: `mùa (sin, cos)   0.033     0.000`
- A: `Gurugram        -0.022     0.228`
- A: `Lucknow         -0.046     0.000`
- A: `Jaipur          -0.098     0.000`
- A: `Bengaluru       -0.124     0.000`
- A: `Amritsar        -0.077     0.000`
- A: `Chennai         -0.117     0.000`
+ B: `mùa (sin, cos)   0.032     0.000`
+ B: `Gurugram        -0.020     0.271`
+ B: `Lucknow         -0.047     0.000`
+ B: `Jaipur          -0.097     0.000`
+ B: `Bengaluru       -0.123     0.000`
+ B: `Amritsar        -0.077     0.001`
+ B: `Chennai         -0.118     0.000`

- A: `so2_0                         Khi SO2 hôm nay cao hơn 10% (tính trên 1 + nồng độ), AQI ngày mai đi cùng với 0,0% (−0,1% đến +0,2%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát 0,5 đến 67,3 µg/m³.`
+ B: `so2_0                         Khi SO2 hôm nay cao hơn 10% (tính trên 1 + nồng độ), AQI ngày mai đi cùng với 0,0% (−0,2% đến +0,2%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát 0,5 đến 67,3 µg/m³.`

- A: `humidity_mean                          Mỗi tăng 10 điểm % của độ ẩm trung bình, AQI ngày mai đi cùng với −1,2% (−2,0% đến −0,3%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát 13,8 đến 96,5 điểm %.`
- A: `pressure_dev     Mỗi tăng 5 hPa của áp suất (lệch so với trung bình 30 ngày trước), AQI ngày mai đi cùng với −1,4% (−4,1% đến +1,3%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −9,6 đến 8,9 hPa.`
- A: `d_pressure                       Mỗi tăng 1 hPa của mức đổi áp suất so với hôm qua, AQI ngày mai đi cùng với −0,6% (−1,4% đến +0,3%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −5,0 đến 7,4 hPa.`
- A: `wind_speed_mean                            Mỗi tăng 1 m/s của tốc độ gió trung bình, AQI ngày mai đi cùng với −1,9% (−3,0% đến −0,8%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát 0,7 đến 8,4 m/s.`
- A: `wind_u                                Mỗi tăng 1 m/s của thành phần gió hướng Đông, AQI ngày mai đi cùng với +1,8% (+1,3% đến +2,2%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −6,8 đến 6,9 m/s.`
- A: `wind_v                                 Mỗi tăng 1 m/s của thành phần gió hướng Bắc, AQI ngày mai đi cùng với −0,5% (−1,2% đến +0,1%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −7,9 đến 5,9 m/s.`
+ B: `humidity_mean                          Mỗi tăng 10 điểm % của độ ẩm trung bình, AQI ngày mai đi cùng với −1,1% (−2,0% đến −0,2%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát 13,8 đến 96,5 điểm %.`
+ B: `pressure_dev     Mỗi tăng 5 hPa của áp suất (lệch so với trung bình 30 ngày trước), AQI ngày mai đi cùng với −1,3% (−3,9% đến +1,4%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −9,6 đến 8,9 hPa.`
+ B: `d_pressure                       Mỗi tăng 1 hPa của mức đổi áp suất so với hôm qua, AQI ngày mai đi cùng với −0,6% (−1,4% đến +0,2%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −5,0 đến 7,4 hPa.`
+ B: `wind_speed_mean                            Mỗi tăng 1 m/s của tốc độ gió trung bình, AQI ngày mai đi cùng với −1,8% (−2,9% đến −0,8%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát 0,7 đến 8,4 m/s.`
+ B: `wind_u                                Mỗi tăng 1 m/s của thành phần gió hướng Đông, AQI ngày mai đi cùng với +1,7% (+1,2% đến +2,2%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −6,8 đến 6,9 m/s.`
+ B: `wind_v                                 Mỗi tăng 1 m/s của thành phần gió hướng Bắc, AQI ngày mai đi cùng với −0,5% (−1,1% đến +0,1%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng đã quan sát −7,9 đến 5,9 m/s.`

- A: `precip_log                                Ngày có 10 mm mưa so với ngày không mưa, AQI ngày mai đi cùng với −9,2% (−11,7% đến −6,5%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng mưa đã quan sát 0 đến 108 mm.`
- A: `mùa (sin, cos)                                         Sau khi giữ các biến còn lại không đổi, hai biến mùa còn cho AQI ngày mai dao động theo mùa với biên độ ±3,4% (đọc hai hệ số sin và cos CHUNG; kiểm định chung hai hệ số p < 0,001).`
- A: `Gurugram                                                                    So với Delhi (mức tham chiếu), Gurugram đi cùng với AQI ngày mai thấp hơn khoảng 2,2% (−5,6% đến +1,4%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
- A: `Lucknow                                                                      So với Delhi (mức tham chiếu), Lucknow đi cùng với AQI ngày mai thấp hơn khoảng 4,5% (−6,6% đến −2,4%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
- A: `Jaipur                                                                       So với Delhi (mức tham chiếu), Jaipur đi cùng với AQI ngày mai thấp hơn khoảng 9,3% (−11,7% đến −7,0%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
+ B: `precip_log                                Ngày có 10 mm mưa so với ngày không mưa, AQI ngày mai đi cùng với −9,2% (−11,8% đến −6,6%, KTC 95%), giữ các biến còn lại trong mô hình không đổi; chỉ trong khoảng mưa đã quan sát 0 đến 108 mm.`
+ B: `mùa (sin, cos)                                         Sau khi giữ các biến còn lại không đổi, hai biến mùa còn cho AQI ngày mai dao động theo mùa với biên độ ±3,3% (đọc hai hệ số sin và cos CHUNG; kiểm định chung hai hệ số p < 0,001).`
+ B: `Gurugram                                                                    So với Delhi (mức tham chiếu), Gurugram đi cùng với AQI ngày mai thấp hơn khoảng 2,0% (−5,4% đến +1,6%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
+ B: `Lucknow                                                                      So với Delhi (mức tham chiếu), Lucknow đi cùng với AQI ngày mai thấp hơn khoảng 4,6% (−6,7% đến −2,4%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
+ B: `Jaipur                                                                       So với Delhi (mức tham chiếu), Jaipur đi cùng với AQI ngày mai thấp hơn khoảng 9,3% (−11,6% đến −6,9%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`

- A: `Amritsar                                                                   So với Delhi (mức tham chiếu), Amritsar đi cùng với AQI ngày mai thấp hơn khoảng 7,4% (−11,4% đến −3,3%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
- A: `Chennai                                                                    So với Delhi (mức tham chiếu), Chennai đi cùng với AQI ngày mai thấp hơn khoảng 11,0% (−14,7% đến −7,3%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
- A: `Hyderabad                                                               So với Delhi (mức tham chiếu), Hyderabad đi cùng với AQI ngày mai thấp hơn khoảng 13,3% (−16,3% đến −10,1%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
+ B: `Amritsar                                                                   So với Delhi (mức tham chiếu), Amritsar đi cùng với AQI ngày mai thấp hơn khoảng 7,4% (−11,3% đến −3,3%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
+ B: `Chennai                                                                    So với Delhi (mức tham chiếu), Chennai đi cùng với AQI ngày mai thấp hơn khoảng 11,1% (−14,7% đến −7,4%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`
+ B: `Hyderabad                                                               So với Delhi (mức tham chiếu), Hyderabad đi cùng với AQI ngày mai thấp hơn khoảng 13,2% (−16,3% đến −10,0%, KTC 95%), giữ các biến còn lại trong mô hình không đổi.`

## Ô 21 (A) / 21 (B), id `5c24a416`: 9 dòng khác, 43 số khác, lệch số lớn nhất 2.06

- A: `Trung bình theo thành phố      64.47  85.15  0.26          95.12             56.82                        -174.74`
- A: `Trung vị cùng tháng (khí hậu)  43.41  64.28  0.58          63.11             38.49                         -84.97`
+ B: `Trung bình theo thành phố      64.54  85.22  0.26          94.96             56.94                        -175.02`
+ B: `Trung vị cùng tháng (khí hậu)  43.44  64.29  0.58          63.10             38.53                         -85.12`

- A: `Ridge L1                       22.94  36.00  0.87          46.58             17.03                           2.25`
- A: `Ridge L2                       20.92  31.89  0.90          42.10             15.63                          10.86`
- A: `Ridge L3                       19.52  30.23  0.91          39.77             14.46                          16.82`
- A: `Ridge L4                       19.08  29.62  0.91          39.14             14.08                          18.67`
- A: `HGB L1                         23.47  37.02  0.86          49.44             16.99                          -0.03`
- A: `HGB L2                         19.02  29.46  0.91          36.50             14.66                          18.93`
- A: `HGB L3                         18.03  28.55  0.92          35.07             13.77                          23.19`
+ B: `Ridge L1                       22.93  35.99  0.87          46.53             17.04                           2.29`
+ B: `Ridge L2                       20.92  31.91  0.90          42.06             15.64                          10.84`
+ B: `Ridge L3                       19.53  30.25  0.91          39.77             14.48                          16.78`
+ B: `Ridge L4                       19.10  29.65  0.91          39.17             14.08                          18.62`
+ B: `HGB L1                         23.00  36.12  0.87          47.38             16.92                           1.98`
+ B: `HGB L2                         19.10  29.67  0.91          36.92             14.65                          18.61`
+ B: `HGB L3                         18.09  28.71  0.92          35.48             13.74                          22.93`

## Ô 22 (A) / 22 (B), id `7ff1c676`: 6 dòng khác, 16 số khác, lệch số lớn nhất 0.12

- A: `Ridge L1  −  Ngày mai = hôm nay            -0.53         -1.19         0.08  chưa tách khỏi 0`
- A: `Ridge L2  −  Ridge L1                      -2.02         -3.06        -1.05       A tốt hơn B`
- A: `Ridge L3  −  Ridge L2                      -1.40         -1.93        -0.93       A tốt hơn B`
- A: `Ridge L3  −  Ridge L1                      -3.42         -4.56        -2.30       A tốt hơn B`
- A: `Ridge L3  −  Ngày mai = hôm nay            -3.95         -5.40        -2.56       A tốt hơn B`
+ B: `Ridge L1  −  Ngày mai = hôm nay            -0.54         -1.20         0.07  chưa tách khỏi 0`
+ B: `Ridge L2  −  Ridge L1                      -2.01         -3.04        -1.05       A tốt hơn B`
+ B: `Ridge L3  −  Ridge L2                      -1.39         -1.92        -0.92       A tốt hơn B`
+ B: `Ridge L3  −  Ridge L1                      -3.40         -4.54        -2.29       A tốt hơn B`
+ B: `Ridge L3  −  Ngày mai = hôm nay            -3.94         -5.39        -2.56       A tốt hơn B`

- A: `HGB L3  −  Ridge L3                        -1.49         -2.21        -0.70       A tốt hơn B`
+ B: `HGB L3  −  Ridge L3                        -1.44         -2.09        -0.73       A tốt hơn B`

## Ô 27 (A) / 27 (B), id `098bb393`: 7 dòng khác, 7 số khác, lệch số lớn nhất 0.1

- A: `Delhi      244        133         36.7       37.1       29.3                       20.2`
- A: `Lucknow    244        111         29.1       29.1       22.7                       22.1`
- A: `Gurugram   244         97         37.1       36.8       30.1                       18.9`
- A: `Amritsar   239         29         29.0       26.7       24.4                       15.9`
- A: `Chennai    244         10         19.4       18.6       17.0                       12.4`
- A: `Jaipur     244          9         16.4       15.7       15.2                        7.3`
+ B: `Delhi      244        133         36.7       37.1       29.3                       20.1`
+ B: `Lucknow    244        111         29.1       29.0       22.7                       22.1`
+ B: `Gurugram   244         97         37.1       36.8       30.1                       18.8`
+ B: `Amritsar   239         29         29.0       26.7       24.4                       16.0`
+ B: `Chennai    244         10         19.4       18.6       17.0                       12.5`
+ B: `Jaipur     244          9         16.4       15.7       15.2                        7.2`

- A: `Hyderabad  244          0         11.4       11.4        9.7                       14.9`
+ B: `Hyderabad  244          0         11.4       11.4        9.7                       15.0`

## Ô 30 (A) / 30 (B), id `35e0efd4`: 2 dòng khác, 5 số khác, lệch số lớn nhất 4

- A: `Validation: 4592 dòng, 1193 ngày nặng. Ngưỡng chọn bằng F2 (recall nặng gấp đôi precision):`
- A: `{'Ngày mai = hôm nay': 160.0, 'Ridge L1': 169.0, 'Ridge L2': 165.0, 'Ridge L3': 166.0, 'Ridge L4': 164.0}`
+ B: `Validation: 4596 dòng, 1196 ngày nặng. Ngưỡng chọn bằng F2 (recall nặng gấp đôi precision):`
+ B: `{'Ngày mai = hôm nay': 160.0, 'Ridge L1': 170.0, 'Ridge L2': 166.0, 'Ridge L3': 167.0, 'Ridge L4': 164.0}`

## Ô 32 (A) / 32 (B), id `e2c7378e`: 5 dòng khác, 36 số khác, lệch số lớn nhất 9

- A: `Ridge L1 (ngưỡng 169)            0.956298   0.78481  0.862109         474     17      102  [0.93; 0.97]     [0.71; 0.84]`
+ B: `Ridge L1 (ngưỡng 170)            0.956298  0.788136  0.864111         472     17      100  [0.93; 0.97]     [0.71; 0.84]`

- A: `Ridge L2 (ngưỡng 165)            0.971722  0.769857  0.859091         491     11      113  [0.95; 0.98]     [0.69; 0.82]`
+ B: `Ridge L2 (ngưỡng 166)            0.969152   0.77572  0.861714         486     12      109  [0.95; 0.98]     [0.70; 0.83]`

- A: `Ridge L3 (ngưỡng 166)            0.969152  0.769388  0.857793         490     12      113  [0.95; 0.98]     [0.70; 0.82]`
+ B: `Ridge L3 (ngưỡng 167)            0.969152  0.778926  0.863688         484     12      107  [0.95; 0.98]     [0.70; 0.83]`

- A: `HGB L3 (ngưỡng 201)              0.912596  0.914948  0.913771         388     34       33  [0.85; 0.95]     [0.87; 0.95]`
- A: `HGB L3 (ngưỡng 164)              0.976864  0.756972  0.852974         502      9      122  [0.95; 0.99]     [0.68; 0.81]`
+ B: `HGB L3 (ngưỡng 201)              0.912596  0.910256  0.911425         390     34       35  [0.85; 0.95]     [0.86; 0.94]`
+ B: `HGB L3 (ngưỡng 166)              0.974293  0.768763   0.85941         493     10      114  [0.94; 0.99]     [0.70; 0.82]`

## Ô 34 (A) / 34 (B), id `acd9840b`: 9 dòng khác, 27 số khác, lệch số lớn nhất 0.011

- A: `                                                                 precision       -0.080        -0.107       -0.056           A kém B`
- A: `                                                                 F1               0.005        -0.017        0.033  chưa tách khỏi 0`
+ B: `                                                                 precision       -0.071        -0.101       -0.045           A kém B`
+ B: `                                                                 F1               0.011        -0.012        0.038  chưa tách khỏi 0`

- A: `                                                                 precision        0.046         0.024        0.074           A hơn B`
- A: `                                                                 F1               0.032         0.017        0.055           A hơn B`
+ B: `                                                                 precision        0.056         0.035        0.083           A hơn B`
+ B: `                                                                 F1               0.038         0.022        0.061           A hơn B`

- A: `                                                                 precision       -0.015        -0.032        0.004  chưa tách khỏi 0`
- A: `                                                                 F1              -0.004        -0.013        0.008  chưa tách khỏi 0`
- A: `mức 3 so với mức 2: riêng phần thời tiết thêm vào                recall          -0.003        -0.009        0.000  chưa tách khỏi 0`
- A: `                                                                 precision       -0.000        -0.014        0.018  chưa tách khỏi 0`
- A: `                                                                 F1              -0.001        -0.011        0.011  chưa tách khỏi 0`
+ B: `                                                                 precision       -0.009        -0.025        0.008  chưa tách khỏi 0`
+ B: `                                                                 F1              -0.000        -0.009        0.009  chưa tách khỏi 0`
+ B: `mức 3 so với mức 2: riêng phần thời tiết thêm vào                recall           0.000        -0.008        0.006  chưa tách khỏi 0`
+ B: `                                                                 precision        0.003        -0.008        0.014  chưa tách khỏi 0`
+ B: `                                                                 F1               0.002        -0.006        0.009  chưa tách khỏi 0`

## Ô 40 (A) / 40 (B), id `1a783eb9`: 1 dòng khác, 1 số khác, lệch số lớn nhất 0.03

- A: `Jaipur, Amritsar               483         38                0.63                   0.63                   0.89                      0.45                 0.84                    0.49`
+ B: `Jaipur, Amritsar               483         38                0.63                   0.63                   0.89                      0.45                 0.84                    0.52`

## Ô 48 (A) / 48 (B), id `fc0d5ea2`: 1 dòng khác, 1 số khác, lệch số lớn nhất 0.1

- A: `Ridge L2            13.9  23.0            98.0`
+ B: `Ridge L2            13.9  23.0            98.1`

## Ô 51 (A) / 51 (B), id `2073a84f`: 3 dòng khác, 5 số khác, lệch số lớn nhất 0.04

- A: `nhỏ nhất                 -3.52                     -4.02`
- A: `trung vị                 -3.41                     -3.93`
- A: `lớn nhất                 -3.30                     -3.81`
+ B: `nhỏ nhất                 -3.48                     -4.00`
+ B: `trung vị                 -3.39                     -3.92`
+ B: `lớn nhất                 -3.30                     -3.83`

## Ô 52 (A) / 52 (B), id `da84d4dc`: 2 dòng khác, 6 số khác, lệch số lớn nhất 0.03

- A: `Bỏ Gurugram (thời tiết gần trùng Delhi): MAE hôm nay 21.51, mức 1 20.98, mức 3 18.16`
- A: `  mức 3 − hôm nay: -3.36 (KTC 95% -4.63 đến -2.11) · mức 3 − mức 1: -2.83 (-3.93 đến -1.77)`
+ B: `Bỏ Gurugram (thời tiết gần trùng Delhi): MAE hôm nay 21.51, mức 1 20.98, mức 3 18.17`
+ B: `  mức 3 − hôm nay: -3.34 (KTC 95% -4.61 đến -2.10) · mức 3 − mức 1: -2.81 (-3.90 đến -1.77)`

## Ô 53 (A) / 53 (B), id `5bad2128`: 54 dòng khác, 3 số khác, lệch số lớn nhất 1946.99

- A: `     MAE (đặt lại NaN, dùng trong notebook)  MAE (giữ ô nội suy)  chênh`
- A: `mức`
- A: `L2                                    20.92                20.92   0.01`
- A: `L3                                    19.52                19.55   0.03`
- A: `1.1% số dòng có ít nhất một chất ô nhiễm bị đổi giá trị bởi bước đặt lại NaN.`
+ B: `biến thể               A. hồi cứu (mã cũ), cohort hồi cứu B. dự báo từ raw (mã mới), bỏ mẫu chỉ có ở raw C. dự báo từ raw (mã mới), cohort raw`
+ B: `n train                                              5741                                           5741                                  5746`
+ B: `n test                                               1947                                           1947                                  1947`
+ B: `n 03-07/2020                                          975                                            975                                   975`
+ B: `ngày nặng train                                      1432                                           1432                                  1436`
+ B: `ngày nặng test                                        389                                            389                                   389`
+ B: `alpha L1                                               10                                             10                                    10`
+ B: `alpha L2                                              0.1                                            0.1                                   0.1`
+ B: `alpha L3                                               30                                             30                                    30`
+ B: `ngưỡng F2 hôm nay                                   160.0                                          160.0                                 160.0`
+ B: `ngưỡng F2 L1                                        169.0                                          170.0                                 170.0`
+ B: `ngưỡng F2 L2                                        165.0                                          165.0                                 166.0`
+ B: `ngưỡng F2 L3                                        166.0                                          166.0                                 167.0`
+ B: `MAE test hôm nay                                23.466359                                      23.466359                             23.466359`
+ B: `MAE test L1                                     22.937281                                      22.935445                             22.929907`
+ B: `MAE test L2                                     20.918858                                      20.920674                             20.921551`
+ B: `MAE test L3                                     19.519018                                      19.519224                             19.528496`
+ B: `MAE 03-07/2020 hôm nay                          14.803077                                      14.803077                             14.803077`
+ B: `MAE 03-07/2020 L1                               14.084705                                      14.089626                             14.088574`
+ B: `MAE 03-07/2020 L2                               13.879546                                      13.883765                             13.878653`
+ B: `MAE 03-07/2020 L3                               13.783362                                      13.787902                             13.773707`
+ B: `L1@201 TP/FP/FN                                 340/53/49                                      339/53/50                             340/53/49`
+ B: `L1@F2 TP/FP/FN                                 372/102/17                                     372/100/17                            372/100/17`
+ B: `L2@201 TP/FP/FN                                 339/43/50                                      339/43/50                             339/43/50`
+ B: `L2@F2 TP/FP/FN                                 378/113/11                                     377/114/12                            377/109/12`
+ B: `L3@201 TP/FP/FN                                 346/40/43                                      346/40/43                             346/40/43`
+ B: `L3@F2 TP/FP/FN                                 377/113/12                                     378/113/11                            377/107/12`
+ B: `Hiệu MAE so cặp giữa các biến thể (chỉ tính khi CÙNG khoá và CÙNG nhãn), bootstrap theo khối 14 ngày lịch:`
+ B: `   so sánh (A trừ B)         tập mức  n (A)  n (B)  cùng khoá  cùng nhãn    ΔMAE  KTC 95% thấp  KTC 95% cao  max |lệch dự đoán|`
+ B: `0            B. − A.        test  L1   1947   1947       True       True -0.0018       -0.0100       0.0063              0.7528`
+ B: `1            B. − A.        test  L2   1947   1947       True       True  0.0018       -0.0074       0.0108              0.7625`
+ B: `2            B. − A.        test  L3   1947   1947       True       True  0.0002       -0.0069       0.0071              0.7935`
+ B: `3            B. − A.  03-07/2020  L1    975    975       True       True  0.0049       -0.0021       0.0116              0.8992`
+ B: `4            B. − A.  03-07/2020  L2    975    975       True       True  0.0042       -0.0012       0.0114              0.4920`
+ B: `5            B. − A.  03-07/2020  L3    975    975       True       True  0.0045       -0.0031       0.0128              0.4167`
+ B: `6            C. − A.        test  L1   1947   1947       True       True -0.0074       -0.0187       0.0029              0.8526`
+ B: `7            C. − A.        test  L2   1947   1947       True       True  0.0027       -0.0122       0.0157              1.6105`
+ B: `8            C. − A.        test  L3   1947   1947       True       True  0.0095       -0.0052       0.0237              1.4312`
+ B: `9            C. − A.  03-07/2020  L1    975    975       True       True  0.0039       -0.0057       0.0129              0.9916`
+ B: `10           C. − A.  03-07/2020  L2    975    975       True       True -0.0009       -0.0156       0.0121              1.1354`
+ B: `11           C. − A.  03-07/2020  L3    975    975       True       True -0.0097       -0.0277       0.0041              1.1054`
+ B: `12           C. − B.        test  L1   1947   1947       True       True -0.0055       -0.0173       0.0031              1.1946`
+ B: `13           C. − B.        test  L2   1947   1947       True       True  0.0009       -0.0097       0.0104              1.3549`
+ B: `14           C. − B.        test  L3   1947   1947       True       True  0.0093       -0.0033       0.0213              1.3134`
+ B: `15           C. − B.  03-07/2020  L1    975    975       True       True -0.0011       -0.0084       0.0071              0.4944`
+ B: `16           C. − B.  03-07/2020  L2    975    975       True       True -0.0051       -0.0181       0.0066              0.8065`
+ B: `17           C. − B.  03-07/2020  L3    975    975       True       True -0.0142       -0.0317       0.0013              0.8606`
+ B: `Trên 8,663 khoá chung của hai đường: AQI hôm nay khác 0 ô, nhãn khác 0 ô. Các cột đặc trưng có ô khác nhau (dung sai 1e-9):`
+ B: `        ô khác  khác do một bên NaN  max |lệch| (hai bên có giá trị)  ô khác: train  ô khác: test  ô khác: lockdown`
+ B: `cột`
+ B: `aqi_1        2                    2                         0.000000              2             0                 0`
+ B: `aqi_2        4                    4                         0.000000              4             0                 0`
+ B: `aqi_wk      22                    0                         0.466288             22             0                 0`
+ B: `co_0        35                    4                         0.875469             35             0                 0`

## Ô 54 (A) / 54 (B), id `296ab635`: 2 dòng khác, 2 số khác, lệch số lớn nhất 0.02

- A: `07-11/2019 (mưa, sau mưa)   1222        178        20.67      20.47      17.98`
- A: `12/2019-02/2020 (mùa đông)   725        211        28.17      27.10      22.12`
+ B: `07-11/2019 (mưa, sau mưa)   1222        178        20.67      20.46      17.98`
+ B: `12/2019-02/2020 (mùa đông)   725        211        28.17      27.10      22.14`

## Ô 55 (A) / 55 (B), id `09edbe64`: 1 dòng khác, 6 số khác, lệch số lớn nhất 0.02

- A: `Bỏ hai biến mùa (sin, cos): MAE mức 1 23.14, mức 3 19.60, chênh -3.53  (có biến mùa: 22.94, 19.52, chênh -3.42)`
+ B: `Bỏ hai biến mùa (sin, cos): MAE mức 1 23.13, mức 3 19.62, chênh -3.51  (có biến mùa: 22.93, 19.53, chênh -3.40)`

## Ô 58 (A) / 58 (B), id `e084a76b`: 1 dòng khác, 0 số khác, lệch số lớn nhất 0

- A: `Mọi con số trong bảng phát hiện khớp với kết quả vừa tính.`
+ B: `181 con số thực nghiệm đã đối chiếu, 181 ở chế độ bắt buộc khớp; 0 chỗ lệch ở chế độ bắt buộc khớp, 0 chỗ lệch được ghi lại (đầu vào khác snapshot).`

