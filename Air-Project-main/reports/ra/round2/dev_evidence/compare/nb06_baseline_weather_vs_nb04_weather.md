# So output dạng chữ của hai bản notebook đã chạy

- A: `/home/user/scratch/ev/chains/nb06_only/executed/06_predict_aqi.ipynb`
- B: `/home/user/scratch/ev/chains/nb04/executed/06_predict_aqi.ipynb`

Tổng: 27 ô mã chung, 10 ô có output dạng chữ khác, 19 dòng khác, 37 số khác (trên các dòng ghép được), lệch số lớn nhất 159.

| Ô (A) | Ô (B) | id | dòng khác | số khác | lệch số lớn nhất | hình A | hình B |
|---|---|---|---|---|---|---|---|
| 3 | 3 | `60ee5880` | 2 | 0 | 0 | 0 | 0 |
| 5 | 5 | `23317e4a` | 0 | 0 | 0 | 0 | 0 |
| 6 | 6 | `4b6742a3` | 0 | 0 | 0 | 0 | 0 |
| 9 | 9 | `f1d19bbb` | 0 | 0 | 0 | 0 | 0 |
| 10 | 10 | `284a1f9e` | 0 | 0 | 0 | 0 | 0 |
| 13 | 13 | `418fa316` | 1 | 1 | 0.01 | 0 | 0 |
| 15 | 15 | `023e10d4` | 0 | 0 | 0 | 1 | 1 |
| 18 | 18 | `4bd5bbdc` | 2 | 2 | 0.001 | 0 | 0 |
| 21 | 21 | `5c24a416` | 1 | 5 | 0.14 | 0 | 0 |
| 22 | 22 | `7ff1c676` | 1 | 3 | 0.05 | 0 | 0 |
| 24 | 24 | `36afa4a5` | 0 | 0 | 0 | 1 | 1 |
| 27 | 27 | `098bb393` | 0 | 0 | 0 | 1 | 1 |
| 30 | 30 | `35e0efd4` | 0 | 0 | 0 | 0 | 0 |
| 32 | 32 | `e2c7378e` | 2 | 12 | 4 | 0 | 0 |
| 34 | 34 | `acd9840b` | 0 | 0 | 0 | 0 | 0 |
| 37 | 37 | `f2ab0f4f` | 0 | 0 | 0 | 1 | 1 |
| 40 | 40 | `1a783eb9` | 0 | 0 | 0 | 0 | 0 |
| 43 | 43 | `c30ab3a0` | 1 | 1 | 0.01 | 0 | 0 |
| 45 | 45 | `ca8502bb` | 0 | 0 | 0 | 1 | 1 |
| 48 | 48 | `fc0d5ea2` | 0 | 0 | 0 | 0 | 0 |
| 51 | 51 | `2073a84f` | 0 | 0 | 0 | 0 | 0 |
| 52 | 52 | `da84d4dc` | 0 | 0 | 0 | 0 | 0 |
| 53 | 53 | `5bad2128` | 7 | 11 | 0.0004 | 0 | 0 |
| 54 | 54 | `296ab635` | 0 | 0 | 0 | 0 | 0 |
| 55 | 55 | `09edbe64` | 0 | 0 | 0 | 0 | 0 |
| 58 | 58 | `e084a76b` | 1 | 1 | 159 | 0 | 0 |
| 59 | 59 | `r2f01sum1` | 1 | 1 | 159 | 0 | 0 |

## Ô 3 (A) / 3 (B), id `60ee5880`: 2 dòng khác, 0 số khác, lệch số lớn nhất 0

- A: `  thời tiết theo ngày: sha256 45f3579a222c55c0 | snapshot 45f3579a222c55c0 | TRÙNG`
+ B: `  thời tiết theo ngày: sha256 2c906e617ec965fe | snapshot 45f3579a222c55c0 | KHÁC snapshot`

- A: `  => mọi đầu vào đúng snapshot: mọi con số thực nghiệm phải khớp.`
+ B: `  => có đầu vào KHÁC snapshot: con số nào phụ thuộc đầu vào đó chỉ được đối chiếu và ghi lại chỗ lệch; con số chỉ phụ thuộc các đầu vào còn trùng snapshot vẫn phải khớp.`

## Ô 13 (A) / 13 (B), id `418fa316`: 1 dòng khác, 1 số khác, lệch số lớn nhất 0.01

- A: `Breusch-Pagan LM                           420.10              316.05`
+ B: `Breusch-Pagan LM                           420.10              316.06`

## Ô 18 (A) / 18 (B), id `4bd5bbdc`: 2 dòng khác, 2 số khác, lệch số lớn nhất 0.001

- A: `so2_0            0.000     0.985`
+ B: `so2_0            0.000     0.984`

- A: `blh_mean         0.000     0.782`
+ B: `blh_mean         0.000     0.781`

## Ô 21 (A) / 21 (B), id `5c24a416`: 1 dòng khác, 5 số khác, lệch số lớn nhất 0.14

- A: `HGB L3                         18.09  28.71  0.92          35.48             13.74                          22.93`
+ B: `HGB L3                         18.12  28.73  0.92          35.50             13.78                          22.79`

## Ô 22 (A) / 22 (B), id `7ff1c676`: 1 dòng khác, 3 số khác, lệch số lớn nhất 0.05

- A: `HGB L3  −  Ridge L3                        -1.44         -2.09        -0.73       A tốt hơn B`
+ B: `HGB L3  −  Ridge L3                        -1.41         -2.07        -0.68       A tốt hơn B`

## Ô 32 (A) / 32 (B), id `e2c7378e`: 2 dòng khác, 12 số khác, lệch số lớn nhất 4

- A: `HGB L3 (ngưỡng 201)              0.912596  0.910256  0.911425         390     34       35  [0.85; 0.95]     [0.86; 0.94]`
- A: `HGB L3 (ngưỡng 166)              0.974293  0.768763   0.85941         493     10      114  [0.94; 0.99]     [0.70; 0.82]`
+ B: `HGB L3 (ngưỡng 201)              0.915167  0.910486  0.912821         391     33       35  [0.85; 0.95]     [0.86; 0.94]`
+ B: `HGB L3 (ngưỡng 167)              0.971722  0.773006  0.861048         489     11      111  [0.94; 0.99]     [0.70; 0.82]`

## Ô 43 (A) / 43 (B), id `c30ab3a0`: 1 dòng khác, 1 số khác, lệch số lớn nhất 0.01

- A: `Lucknow       244        111    -0.15   [-0.31; 0.02]       -0.01  [-0.16; 0.14]            50.59           40.00           10.59  [-17; 35]`
+ B: `Lucknow       244        111    -0.15   [-0.31; 0.02]       -0.01  [-0.16; 0.15]            50.59           40.00           10.59  [-17; 35]`

## Ô 53 (A) / 53 (B), id `5bad2128`: 7 dòng khác, 11 số khác, lệch số lớn nhất 0.0004

- A: `MAE test L3                                     19.519018                                      19.519224                             19.528496`
+ B: `MAE test L3                                     19.519175                                      19.519382                             19.528656`

- A: `MAE 03-07/2020 L3                               13.783362                                      13.787902                             13.773707`
+ B: `MAE 03-07/2020 L3                               13.783268                                      13.787809                             13.773614`

- A: `2            B. − A.        test  L3   1947   1947       True       True  0.0002       -0.0069       0.0071              0.7935`
+ B: `2            B. − A.        test  L3   1947   1947       True       True  0.0002       -0.0069       0.0071              0.7933`

- A: `8            C. − A.        test  L3   1947   1947       True       True  0.0095       -0.0052       0.0237              1.4312`
+ B: `8            C. − A.        test  L3   1947   1947       True       True  0.0095       -0.0052       0.0237              1.4316`

- A: `11           C. − A.  03-07/2020  L3    975    975       True       True -0.0097       -0.0277       0.0041              1.1054`
+ B: `11           C. − A.  03-07/2020  L3    975    975       True       True -0.0097       -0.0277       0.0041              1.1057`

- A: `14           C. − B.        test  L3   1947   1947       True       True  0.0093       -0.0033       0.0213              1.3134`
+ B: `14           C. − B.        test  L3   1947   1947       True       True  0.0093       -0.0033       0.0213              1.3133`

- A: `17           C. − B.  03-07/2020  L3    975    975       True       True -0.0142       -0.0317       0.0013              0.8606`
+ B: `17           C. − B.  03-07/2020  L3    975    975       True       True -0.0142       -0.0317       0.0013              0.8603`

## Ô 58 (A) / 58 (B), id `e084a76b`: 1 dòng khác, 1 số khác, lệch số lớn nhất 159

- A: `181 con số thực nghiệm đã đối chiếu, 181 ở chế độ bắt buộc khớp; 0 chỗ lệch ở chế độ bắt buộc khớp, 0 chỗ lệch được ghi lại (đầu vào khác snapshot).`
+ B: `181 con số thực nghiệm đã đối chiếu, 22 ở chế độ bắt buộc khớp; 0 chỗ lệch ở chế độ bắt buộc khớp, 0 chỗ lệch được ghi lại (đầu vào khác snapshot).`

## Ô 59 (A) / 59 (B), id `r2f01sum1`: 1 dòng khác, 1 số khác, lệch số lớn nhất 159

- A: `181 con số thực nghiệm đã đối chiếu, 181 ở chế độ bắt buộc khớp; 0 chỗ lệch ở chế độ bắt buộc khớp, 0 chỗ lệch được ghi lại (đầu vào khác snapshot).`
+ B: `181 con số thực nghiệm đã đối chiếu, 22 ở chế độ bắt buộc khớp; 0 chỗ lệch ở chế độ bắt buộc khớp, 0 chỗ lệch được ghi lại (đầu vào khác snapshot).`

