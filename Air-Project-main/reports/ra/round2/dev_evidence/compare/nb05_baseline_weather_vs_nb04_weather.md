# So output dạng chữ của hai bản notebook đã chạy

- A: `/home/user/scratch/ev/chains/baseline/executed/05_weather_correlation.ipynb`
- B: `/home/user/scratch/ev/chains/nb04/executed/05_weather_correlation.ipynb`

Tổng: 10 ô mã chung, 1 ô có output dạng chữ khác, 3 dòng khác, 3 số khác (trên các dòng ghép được), lệch số lớn nhất 0.5.

| Ô (A) | Ô (B) | id | dòng khác | số khác | lệch số lớn nhất | hình A | hình B |
|---|---|---|---|---|---|---|---|
| 3 | 3 | `4ffc7ef8` | 0 | 0 | 0 | 0 | 0 |
| 5 | 5 | `00476355` | 0 | 0 | 0 | 0 | 0 |
| 7 | 7 | `924cbf91` | 0 | 0 | 0 | 1 | 1 |
| 10 | 10 | `d3fcf4ab` | 3 | 3 | 0.5 | 0 | 0 |
| 12 | 12 | `026c52af` | 0 | 0 | 0 | 1 | 1 |
| 15 | 15 | `3b546226` | 0 | 0 | 0 | 0 | 0 |
| 17 | 17 | `f50c0d42` | 0 | 0 | 0 | 1 | 1 |
| 19 | 19 | `57430d11` | 0 | 0 | 0 | 1 | 1 |
| 22 | 22 | `c686e4a8` | 0 | 0 | 0 | 0 | 0 |
| 26 | 26 | `3e9ef243` | 0 | 0 | 0 | 0 | 0 |

## Ô 10 (A) / 10 (B), id `d3fcf4ab`: 3 dòng khác, 3 số khác, lệch số lớn nhất 0.5

- A: `Gurugram  H1        361          356                 15.0    [-5.5; 41.8]`
+ B: `Gurugram  H1        361          356                 15.0    [-5.5; 42.1]`

- A: `Jaipur    H1        366          365                 -4.5    [-16.5; 7.7]`
+ B: `Jaipur    H1        366          365                 -4.5    [-16.5; 7.2]`

- A: `Jaipur    H1          0.48                       0.447   chưa đủ bằng chứng`
+ B: `Jaipur    H1          0.48                       0.386   chưa đủ bằng chứng`

