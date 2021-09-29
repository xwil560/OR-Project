\* Tie_Production *\
Maximize
OBJ: 8.22 Ties_AllPoly + 16.24 Ties_AllSilk + 8.77 Ties_PolyCotton
 + 8.66 Ties_SilkCotton
Subject To
Cotton: 0.05 Ties_PolyCotton + 0.044 Ties_SilkCotton <= 1600
Max_AllPoly: Ties_AllPoly <= 14000
Max_AllSilk: Ties_AllSilk <= 7000
Max_PolyCotton: Ties_PolyCotton <= 16000
Max_SilkCotton: Ties_SilkCotton <= 8500
Min_AllPoly: Ties_AllPoly >= 10000
Min_AllSilk: Ties_AllSilk >= 5000
Min_PolyCotton: Ties_PolyCotton >= 13000
Min_SilkCotton: Ties_SilkCotton >= 5000
Polyester: 0.08 Ties_AllPoly + 0.05 Ties_PolyCotton <= 3000
Silk: 0.125 Ties_AllSilk + 0.066 Ties_SilkCotton <= 1200
Bounds
 0 <= Ties_AllPoly
 0 <= Ties_AllSilk
 0 <= Ties_PolyCotton
 0 <= Ties_SilkCotton
Generals
Ties_AllPoly
Ties_AllSilk
Ties_PolyCotton
Ties_SilkCotton
End
