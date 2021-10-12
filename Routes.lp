\* Routes_Problem *\
Minimize
OBJ: 2000 DailyFreight1_0 + 2000 DailyFreight1_1 + 2000 DailyFreight1_2
 + 2000 DailyFreight1_3 + 2000 DailyFreight1_4 + 2000 DailyFreight2_0
 + 2000 DailyFreight2_1 + 2000 DailyFreight2_2 + 2000 DailyFreight2_3
 + 2000 DailyFreight2_4 + 335.25625 Woolworths1_0 + 443.05 Woolworths1_1
 + 452.931875 Woolworths1_2 + 501.45125 Woolworths1_3 + 423.6 Woolworths1_4
 + 335.25625 Woolworths2_0 + 443.05 Woolworths2_1 + 452.931875 Woolworths2_2
 + 501.45125 Woolworths2_3 + 423.6 Woolworths2_4
Subject To
Max_trucks_on_Route_1: Woolworths1_0 + Woolworths1_1 + Woolworths1_2
 + Woolworths1_3 + Woolworths1_4 <= 2
Max_trucks_on_Route_2: Woolworths2_0 + Woolworths2_1 + Woolworths2_2
 + Woolworths2_3 + Woolworths2_4 <= 1
Store_Delivery_MaximumCountdown_Airport: DailyFreight1_0 + DailyFreight2_0
 + Woolworths1_0 + Woolworths2_0 = 1
Store_Delivery_MaximumCountdown_Auckland_City: DailyFreight1_2
 + DailyFreight2_2 + Woolworths1_2 + Woolworths2_2 = 1
Store_Delivery_MaximumCountdown_Aviemore_Drive: DailyFreight1_1
 + DailyFreight2_1 + Woolworths1_1 + Woolworths2_1 = 1
Store_Delivery_MaximumCountdown_Birkenhead: DailyFreight1_3 + DailyFreight2_3
 + Woolworths1_3 + Woolworths2_3 = 1
Store_Delivery_MaximumSuperValue_Palomino: DailyFreight1_4 + DailyFreight2_4
 + Woolworths1_4 + Woolworths2_4 = 1
Binaries
DailyFreight1_0
DailyFreight1_1
DailyFreight1_2
DailyFreight1_3
DailyFreight1_4
DailyFreight2_0
DailyFreight2_1
DailyFreight2_2
DailyFreight2_3
DailyFreight2_4
Woolworths1_0
Woolworths1_1
Woolworths1_2
Woolworths1_3
Woolworths1_4
Woolworths2_0
Woolworths2_1
Woolworths2_2
Woolworths2_3
Woolworths2_4
End
