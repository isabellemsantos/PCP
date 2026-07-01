
/* ===================== DADOS BASE ===================== */
const CPD_DATA = [["00442", "PARAF (+-) MP 2,5x3,7 ZNB triv CH TT"], ["01273", "PARAF MP 3x8 ZNA triv 8.8 DIN"], ["01702", "PARAF MP 3x35(20) ZNA triv DIN"], ["01727", "PARAF MP 3x43 ZNA triv DIN"], ["01845", "PARAF MP 4x8 Geo Prata 8.8"], ["02099", "PARAF MP 4x25 ZNA triv"], ["02158", "PARAF MP #8-32x6,35 UNC s/ acab s/tt"], ["02160", "PARAF MP 4x45 ZNA triv"], ["02171", "PARAF MP 5x7,5 ZNA triv"], ["02195", "PARAF (SL) MP 5x16 ZNA triv"], ["02237", "PARAF MP 5x22 Geo Preto esc Pta.Guia Tork Break"], ["02291", "PARAF (SL) MP 6x20 ZNP triv DIN"], ["02296", "PARAF (SL) MP 6X13 ZNLIX (8.8)"], ["02300", "PARAF (SL) MP 6x13 ZnLix triv. Nylon 180º (8.8)"], ["02518", "PARAF MPW 4x4,5 ZNA triv TT"], ["02532", "PARAF (+ -) MFFW 4x16,5 ZNA triv 9.8 Pta.Guia"], ["04700", "PARAF (SL) MF 4x10,8 ZNA triv  T.T"], ["04758", "PARAF MF 5x16,35 ZNA triv 8.8 Nylon"], ["04760", "MF 5x16 ZnB Triv. (8.8)"], ["04761", "MF 5x16 ZnB Triv. (8.8)"], ["04772", "PARAF MF 6x16 ZNA triv Nylon Patch 180º  8.8"], ["04772.1", "PARAF MF 6x16 ZNA triv Nylon Patch 180º  8.8"], ["04773", "PARAF (SL) MF 6x30 ZNB triv 10.9"], ["04853", "PARAF (+-) MFF 4x18 NI (11) Pta Guia Usi."], ["04875", "PARAF (+-) MFF 4x11 ZnNiB Triv 8.8 CH"], ["04926", "PARAF (SI) MFF 5x40 (22) ZNA triv 10.9"], ["04929", "PARAF (SI) MFF 6x17 ZNA triv 10.9"], ["04957", "PARAF (+-) MFF 4x12 ZNA triv 8.8 pta.guia"], ["04978", "PARAF (SL) MFF 6x16 ZNA triv CH Precot 80 9.8"], ["04980", "PARAF (SI) MFF 6x38(24) ZNA triv recart. 11.9 CH"], ["04991", "(SI) MFF 6x14 ZNA TRIV (8.8)"], ["05001", "PARAF (SI) MFF 16x12 ZnLix Triv 5.8"], ["05020", "PARAF (+-) MO 3x10,8 NI pta guia 8.8"], ["05055", "PARAF (SL) MO 4x9,35 ZNB triv"], ["05055.1", "PARAF (SL) MO 4x9,35 ZNB triv"], ["05070", "PARAF (SL)(ST)  MVW 5x19 ZNNIP TRIV (PTA) CA"], ["05491", "PARAF (SL) BP 2,2x9,5 ZNB triv (V) cab esp"], ["05503", "PARAF (SL) BP 2,2x13 ZNB triv (V) cab esp"], ["06031", "PARAF BP 3x6 ZNA triv"], ["06366", "PARAF BP 3x25 ZNA triv"], ["06572", "PARAF (SL) BP 3,5x34 (19) ZNA Triv 8.8 (V)"], ["06576", "PARAF BP 3,5x43(18) ZNB triv (V)  8.8"], ["06579", "PARAF BP 3,5x22 ZnB Triv (V)"], ["06736", "PARAF BP 5x40 ZNP+fe triv"], ["06757", "PARAF (+-) BP 4,8x25 ZNA triv (V) DIN"], ["06964", "PARAF (+) BUP 4x16 ZNA triv"], ["06966", "PARAF (SL) BUP 4x20 Zna Triv"], ["07004", "PARAF BUPW 6x16 ZNA triv"], ["08246", "PARAF BB 4x16 ZNA triv"], ["09100", "PARAF BO 2,2x9,3 ZNA triv (V)"], ["10387", "PARAF ABP 3,9x13 ZNA triv"], ["10673", "PARAF ABP 4,8x16 ZNP+fe triv"], ["10785", "PARAF S' ABUPW 4,2x20 ZNNIP (Pta Abau.) (AW)"], ["10790", "PARAF S' ABUPW 4,2x25 ZNP TRIV (Pta abau) (AW)"], ["10795", "PARAF (+) ABUPW 6x30 ZNP triv"], ["10987", "PARAF (PZ) ABPW 4,8x16 S/acab"], ["13037", "PARAF S' MP 3x8 ZNA TRIV (CW) (AW) 8.8"], ["13063", "PARAF S' MP 3x10 ZNA triv (CW)(AW) CH 8.8"], ["13064", "PARAF S' MP 3x10 ZNA triv (CW) DIN   8.8"], ["13140", "PARAF S' MP 3x25 ZNB triv (CW)(AW) 8.8 CH"], ["13166", "PARAF S' MP 3,5x7 NI (CW)"], ["13187", "PARAF S' MP 4x7 ZNA triv (CW)"], ["13224", "PARAF S' MP 4x10 ZNA triv (CW)(AW)"], ["13224.1", "PARAF S' MP 4x10 ZNA triv (CW)(AW)"], ["13277", "PARAF S' MP 4x18 ZNP triv (CW)(AW)"], ["13400", "PARAF S' MP 5x8 ZNB triv (CW)"], ["13409", "PARAF S' MP 5x10 ZNA triv (CW)"], ["13421", "PARAF S' MP 5x12 ZNA triv (CW)(AW)"], ["13423", "PARAF S' MP 5x12 ZNB triv (AW)"], ["13499", "PARAF S' MP 5x18 ZNP triv (CW)"], ["13684", "PARAF S' (+) MUP 4x10 ZNA triv (CW)(AW) 8.8 CH"], ["13685", "PARAF S' (+) MUP 4x12 ZNA triv (CW)(AW) 8.8 CH"], ["13688", "PARAF S' (+) MUP 4x14 ZNA triv (CW)(AW) 8.8 CH"], ["13691", "PARAF S' (+) MUP 4x16 ZNA triv (CW)(AW) 8.8 CH"], ["13695", "PARAF S' (+) MUP 4x20 ZNA triv (CW)(AW) 8.8 CH"], ["13707", "PARAF S' (+) MUP 5x8 ZNA triv 8.8 CH (CW)(AW)"], ["13710", "PARAF S' (+) MUP 5x10 ZNA triv (CW)(AW) 8.8"], ["13711", "PARAF S' (+) MUP 5x12 ZNA triv (CW)(AW) 8.8 CH"], ["13715", "PARAF S' (+) MUP 5x16 ZNA triv (CW)(AW) 8.8 CH"], ["13716", "PARAF S' (+) MUP 5x20 ZNA triv (CW)(AW) 8.8 CH"], ["13718", "PARAF S' (+) MUP 5x25 G PRATA (CW)(AW)"], ["13739", "PARAF S' (+) MUP 6x16 G PRATA (CW)(AW)"], ["13742", "PARAF S' (+) MUP 6x12 ZNA triv (CW)(AW)  8.8"], ["13744", "PARAF S' (+) MUP 6x16 ZNA triv (CW)(AW)  8.8"], ["13747", "PARAF S' (+) MUP 6x25 ZNA triv (CW)(AW)  8.8"], ["13748", "PARAF S' (+) MUP 6x30 ZNA triv (CW)(AW)  8.8"], ["13754", "PARAF S' (+) MUP 6x20 ZNA triv (CW)(AW) 8.8"], ["13763", "PARAF S' (+) MUP 6x16 ZNA triv (CW)(AW) 8.8 Nylon C"], ["13766", "PARAF S' (+) MUP 6x20 ZNA triv (CW)(AW) 8.8 Nylon C"], ["13767", "PARAF S' MUP 6x20 ZNP triv (IW) pta guia"], ["13792", "PARAF S'MLH 8X20 ZnA Triv 8.8 (AW)"], ["13800", "PARAF S' (+) MUP 6x16(12) ZNP triv Pta Guia (AW)"], ["13801", "PARAF S' (+) MUP 6x20 Geo Prata (CW)(AW)"], ["13802", "PARAF S' (+) MUP 6x34 G (AW) pta. guia"], ["13803", "PARAF S' (+) MUP 6x35(20) G Prata 8.8 (CW)( AW)"], ["13814", "PARAF S' MUP 8x21,5 ZnB Triv (IW) Pta guia Ch"], ["13833", "PARAF S' (+) MUP 8x25 ZNB triv (CW)(AW) 8.8 CH"], ["13837", "PARAF S' (+) MUP 8x35 ZNA triv (CW)(AW) 8.8 CH"], ["13838", "PARAF S' (+) MUP 8x30 G PRATA (CW)(AW)"], ["13839", "PARAF S' (+) MUP 8x30 G PRATA (CW)(AW) PLUS"], ["13861", "PARAF S' (+) BUP 5x16 ZNA triv (AW)"], ["13870", "PARAF S' (+) BUP 6x16 G prata + PLUS  (AW)"], ["14047", "PARAF (SL) MFF 3x4 DECAP. ON 8.8  CH"], ["14048", "PARAF (SL) MFF 3x4 ZNA TRIV  8.8  CH"], ["16618", "PREGO 3,2x6 ZNP triv"], ["16696", "PINO FF 4x83,5 ZNB triv"], ["16696.1", "PINO FF 4x83,5 ZNB triv"], ["16698", "PINO FF 4,15x83,3 Znb Tri  usin c/ corpo recartilho"], ["16710", "PRISION.(M6x20)x(M6X20)X 48 Pta.Guia ZNP triv10.9"], ["16712", "PINO 6x43 ZNB triv"], ["16715", "PINO 6x110 ZNB triv C/ CANAL USINADO"], ["16716", "PINO FF (SL) 4,4X15,3 Zn triv cab.rosca 5/16-32"], ["16745", "REBITE FF 9x15,8 ZNB triv c/ colar"], ["16829", "PRISION LH (M#10-32 UNF2A X35,1(M#1/4-28UNF2A) OXID"], ["16870", "PARAF MS 6x22,79 ZNA triv pta guia"], ["16871", "PARAF MS 5x13,8 (11,7) ZnNiB triv pta.guia 8.8"], ["16895", "PARAF MS 8x25 ZNA triv +TOP 10.9 CH"], ["17220", "PARAF (SL) PP1DP 2,6-24x8 ZNA triv"], ["18001", "PP1DUPWR 7X18 ZnB Triv."], ["18100", "(SL) PP1DP 6X30 ZnB Triv. (Torque Break)"], ["19648", "PARAF PP1DF 3,5-19x12 ZNB triv"], ["19800", "PARAF (+/-) PP1DFF 3,5-19 x18(8) ZNA triv"], ["21029", "PARAF BT 4x14 ZNP Triv"], ["21070", "PARAF (SI) MFFW 5x14 s/ acab. 10.9"], ["21460", "PARAF (SI) MFF 6x32(17) DECAP 8.8 c/corpo"], ["21460.2", "PARAF (SI) MFF 6x32(17) DECAP 8.8 c/corpo"], ["21488", "PARAF MPW 5X50(40,9) ZNP Triv (c/ CANAL) (PONTA)"], ["21491", "PARAF MPW 5X50(40,9) ZNP Triv (PONTA RAIADA)"], ["21887", "PARAF MUP 5x12 DECAP 8.8"], ["21887.1", "PARAF MUP 5x12 DECAP 8.8"], ["21911", "PARAF MLH 8x11(18,2) 8.8 Decap. c/corpo"], ["21911/1", "PARAF MLH 8x11(18,2) 8.8 Decap. c/corpo"], ["21912", "PARAF MLH 8x11(20,2) 8.8 Decap"], ["21914", "PRISIONEIRO MLH 8x41 Decap 8.8 c/corpo"], ["21914.2", "PRISIONEIRO MLH 8 x 41  Decap 8.8 c/corpo"], ["21915", "PRISIONEIRO MLH 8x15 DECAP 8.8 cab esp"], ["21915/2", "PRISIONEIRO MLH 8x15 DECAP 8.8 cab esp"], ["21921", "PARAF MLHWRO 8x20 Cr polido CH 8.8"], ["21921.3", "PARAF MLHWRO 8x20 Cr polido CH 8.8"], ["21936", "PARAF MLHW 8x35,5 (18) Cr 8.8"], ["21936.1", "PARAF MLHW 8x35,5 (18) Cr 8.8"], ["21936.2", "PARAF MLHW 8x35,5 (18) Cr 8.8"], ["21936.3", "PARAF MLHW 8x35,5 (18) Cr 8.8"], ["21936.4", "PARAF MLHW 8x35,5 (18) Cr 8.8"], ["21946", "PARAF MUPW 6x15,8(11) Decap. 8.8"], ["21960", "PARAF MUPW 6x16,6(14) Decap 8.8"], ["21960.4", "PARAF MUPW 6x16,6(14) Enegr. 8.8"], ["21960/1", "PARAF MUPW 6x16,6(14) Enegr. 8.8"], ["24050", "PARAF (+/-) MP 5X72(20) Zna Triv C/Corpo 8.8"], ["26168", "PARAF MLH 6x29,1 (7) ZnLiX Triv  9.8"], ["26188", "PARAF MUPWR 5x78(20) ZNB Lix triv 6.8"], ["26210", "MFF 10x70 (Recartilho dup lo) (CorpoØ12)  Decap ON"], ["26215", "MFF10x80(Recartilho Duplo ) (CorpoØ12) Decap ON"], ["26464", "PARAF MUPWR 5x70(20) ZNB triv 8.8"], ["26469", "PARAF MUPWR 5x88(20) ZNB triv 8.8 corpo"], ["26600", "PARAF MUPWR 12x20 CH ZNA triv 1010"], ["26850", "PARAF MLHO 6x30(13) ZNB 8.8 CH"], ["26950", "PARAF (SL)(ST) MP 2,5x6 ZNB Lix Pta.Conica"], ["26973", "PARAF (SL)(ST) MP 2,5x14 ZNB triv"], ["27000", "PARAF (ST) MP 3x6(5) ZNLIX TRIV"], ["27109", "PARAF (SL)(ST) MP 3x10 ZNP triv"], ["27130", "PARAF (SL) MP 3x22,8(8) Zna Triv 8.8 C/ CORPO"], ["27399", "PARAF (ST) MP 4x8 ZNA triv"], ["27420", "PARAF (ST) MP 4x10 ZNA triv"], ["27593", "PARAF (SL)(ST) MP 5x20 ZNA triv"], ["27626", "PARAF (SL)(ST) MP 6x16 (14) Geo Prata 8.8"], ["27682", "PARAF(SL) MPW 3x6,7 DECAP ON 8.8  CH"], ["27701", "PARAF (ST) MPW 4x8 ZNP triv"], ["27717", "PARAF (SL) MF 2,5x8 ZNB triv  TT"], ["27745", "PARAF (SL)(ST) MF 4x10 ZNA triv Cab.Maior"], ["27770", "PARAF (SL)(ST) MO 5x12 ZNA triv"], ["27855", "PARAF (SL)(ST) MFF 2,5x6 ZNA triv"], ["27859", "PARAF (SL)(ST) MFF 3x8 ZinKlad  8.8"], ["27862", "PARAF (SL)(ST) MFF 3x8 ZnA Triv  8.8"], ["27885", "PARAF (SL)(ST) MFF 5x17,5 Delt Prata torque 8.8"], ["27980", "PARAF (SL)(ST) MV 4x12 ZNA triv Din"], ["27999", "PARAF (SL) MT 4x10 ZNP triv"], ["28019", "PARAF (SL)(PT) PP1DP 2,2 x6,2 ZinkLad Pta CA"], ["28020", "PARAF (PT) PP1DF 2-28x8 ZNB Triv  (Cab Menor)"], ["28200", "PARAF (PT) PP1DB 3-20x14 ZNB triv"], ["30096", "PARAF S(SI) MT 6x16 INOX CH (AW INOX)"], ["30200", "MP 5x12 Geo Preto + Plus (5.8)  DIN"], ["30453", "PARAF MT 5x12 ZnLix triv CH cab.maior"], ["30460", "PARAF MT 5x14 ZNP+fe triv"], ["30510", "PARAF BP 5x20 ZNP triv+Sel"], ["30893", "PARAF MLH 6x16 ZNP triv"], ["30982", "PARAF MUPW 8x20 ZN triv CH 8.8"], ["30989", "PARAF MUPWR 8x20 ZN triv CH 8.8"], ["31001", "PARAF BP 4x8 ZNA triv +SEL (V)"], ["31001.2", "PARAF BP 4x8 ZNA triv +SEL (V)"], ["31002", "PARAF BP 4x10 ZNB triv+SEL(V)"], ["31002.1", "PARAF BP 4x10 ZNB triv+SEL(V)"], ["31005", "PARAF BP 3x12 ZNA triv+SEL (V)"], ["31005.3", "PARAF BP 3x12 ZNA triv+SEL (V)"], ["31005.4", "PARAF BP 3x12 ZNA triv+SEL (V)"], ["31009", "PARAF BP 4x12 ZnLix triv"], ["31013", "PARAF BP 5x8 ZNP triv"], ["31013.2", "PARAF BP 5x8 ZNP+fe triv"], ["31013/1", "PARAF BP 5x8 ZNP+fe triv"], ["31015", "PARAF BP 5x12 ZNA triv+ SEL"], ["31015.2", "PARAF BP 5x12 ZNA triv+ SEL"], ["31016", "PARAF BP 5x12 ZNB Triv (V)"], ["31019", "PARAF BT 4x10 ZNP+fe triv"], ["31022", "PARAF BT 4x10 ZNP+fe (V) triv"], ["31024", "PARAF BT 4x10 ZNB triv+ sel"], ["31026", "PARAF BT 4x12 ZNA triv"], ["31026.4", "PARAF BT 4x12 ZNA triv"], ["31027", "PARAF BT 4x12 ZNP triv (V)"], ["31028", "PARAF BT 4x12 ZNP triv"], ["31028.3", "PARAF BT 4x12 ZNP triv"], ["31028.4", "PARAF BT 4x12 ZNP triv"], ["31028/1", "PARAF BT 4x12 ZNP triv"], ["31029", "* PARAF BT 4x14 ZNP triv"], ["31031", "PARAF BT 4x20 ZnLix"], ["31032", "PARAF BT 4x12 ZNA triv (V)"], ["31032.2", "PARAF BT 4x12 ZNA triv (V)"], ["31033", "PARAF BT 4x16 ZnLix triv (V)"], ["31034", "PARAF BT 4x12 ZNP triv (V)"], ["31035", "PARAF BT 4x16 ZNP triv (V)"], ["31036", "PARAF BT 4x16 ZnLix triv+sel"], ["31037", "PARAF BT 4x16 ZNP triv"], ["31037.1", "PARAF BT 4x16 ZNP triv"], ["31038", "PARAF BT 5x12 ZNP+fe triv"], ["31038.3", "PARAF BT 5x12 ZNP+fe triv"], ["31039", "PARAF BT 5x12 ZNB triv"], ["31039.1", "PARAF BT 5x12 ZNB triv"], ["31039.2", "PARAF BT 5x12 ZNB triv"], ["31039/1", "PARAF BT 5x12 ZNB triv"], ["31040", "PARAF BT 5x12 ZnLix triv (V)"], ["31040.1", "PARAF BT 5x12 ZnLix triv (V)"], ["31040.2", "PARAF BT 5x12 ZnLix triv (V)"], ["31041", "PARAF BT 5x10 ZnP Triv"], ["31043", "PARAF BT 5x16 ZNA triv"], ["31043.3", "PARAF BT 5x16 ZNA triv"], ["31043.4", "PARAF BT 5x16 ZNA triv"], ["31044", "PARAF BT 5x16 ZNP+fe triv"], ["31044.2", "PARAF BT 5x16 ZNP+fe triv"], ["31044.3", "PARAF BT 5x16 ZNP+fe triv"], ["31044/1", "PARAF BT 5x16 ZNP+fe triv"], ["31046", "PARAF BT 5x20 ZNB triv"], ["31046.2", "PARAF BT 5x20 ZNB triv"], ["31047", "PARAF BT 5x25 ZNB triv"], ["31047.2", "PARAF BT 5X25 ZNB TRIV"], ["31048", "PARAF BT 5x30 ZNB triv"], ["31048.1", "PARAF BT 5X30 ZNB TRIV"], ["31049", "PARAF BT 5x20 ZNP triv"], ["31049.1", "PARAF BT 5x20 ZNP triv"], ["31055", "PARAF ABP 4x10 ZNA triv"], ["31071", "PARAF (SI) MFFW 6x23(18) ZNB triv 10.9"], ["31073", "PINO 6X48  S/ ACAB"], ["31074", "PINO FF 6x31,5 ZNB triv c/ furo usinado"], ["31074.3", "PINO FF 6x31,5 ZNB triv c/ furo usinado"], ["31076", "PINO FF 8x33 ZNB triv 8.8 CH furo usinado"], ["31076.3", "PINO FF 8x33 ZNB triv 8.8 CH furo usinado"], ["31077", "PINO FF 8x35,8 ZNB triv usin cortado 8.8"], ["31077.1", "PINO FF 8x35,8 ZNB triv usin cortado 8.8"], ["31078", "PINO FF 8x38,5 ZNB triv furo usinado"], ["31078.1", "PINO FF 8x38,5 ZNB triv furo usinado"], ["31079", "PINO FF 8x41,5 Geo Prata furo usinado"], ["31079.1", "PINO FF 8x41,5 Geo Prata furo usinado"], ["31084", "PINO FF 8x71 ZNB triv furo usinado"], ["31084.1", "PINO FF 8x71 ZNB triv furo usinado"], ["31084.2", "PINO FF 8x71 ZNB triv furo usinado"], ["31090", "PARAF MP 3x8 ZNA triv 8.8"], ["31115", "PARAF MPx 4x12 ZNP+fe triv"], ["31145", "PARAF MPx 4x32 ZNP+fe triv   8.8"], ["31145.2", "PARAF MPx 4x32 ZNP+fe triv   8.8"], ["31145/1", "PARAF MPx 4x32 ZNP+fe triv  8.8"], ["31147", "PARAF MPx 4x45(40) ZNP triv 8.8"], ["31147.2", "PARAF MPx 4x45(40) ZNP triv  8.8"], ["31147/1", "PARAF MPx 4x45(40) ZNP triv  8.8"], ["31149", "PARAF MPx 5x8 ZNB triv"], ["31155", "PARAF MPx 5x10 ZNA triv  8.8"], ["31155.1", "PARAF MPx 5x10 ZNA triv  8.8"], ["31165", "PARAF MPx 5x12 ZNB triv 8.8"], ["31185", "PARAF MPx 5x16 ZNP triv   8.8"], ["31185.2", "PARAF MPx 5x16 ZNP triv   8.8"], ["31185.3", "PARAF MPx 5x16 ZNP triv  8.8"], ["31195", "PARAF MPx 5x18 ZNP TRIV 8.8"], ["31195.5", "PARAF MPx 5x18 ZNP triv  8.8"], ["31195/1", "PARAF MPx 5x18 ZNP triv   8.8"], ["31195/2", "PARAF MPx 5x18 ZNP triv  8.8"], ["31200", "PARAF MPx 5x20 ZNB triv+ SEL 8.8"], ["31200.3", "PARAF MPx 5x20 ZNB triv+ sel      8.8"], ["31205", "PARAF MPx 5x20 ZNP triv 8.8"], ["31205.3", "PARAF MPx 5x20 ZNP triv  8.8"], ["31205/1", "PARAF MPx 5x20 ZNP triv 8.8"], ["31210", "PARAF MPx 5x22 ZNP triv 8.8"], ["31210.4", "PARAF MPx 5x22 ZNP triv  8.8"], ["31212", "PARAF MPx 5x22 ZNB triv 8.8"], ["31230", "PARAF MPx 5x25 ZNP triv"], ["31240", "PARAF MPx 5x28 ZNP triv 8.8"], ["31240.3", "PARAF MPx 5x28 ZNP triv   8.8"], ["31240.4", "PARAF MPx 5x28 ZNP triv  8.8"], ["31240/1", "PARAF MPx 5x28 ZNP triv   8.8"], ["31245", "PARAF MPx 5x30 ZNP+fe triv"], ["31247", "PARAF MPx 5x32 ZNP TRIV 8.8"], ["31258", "PARAF MPx 5x60 ZNP triv 8.8"], ["31258.1", "PARAF MPx 5x60 ZNP triv 8.8"], ["31325", "PARAF MPx 6x10 ZNP+fe triv Dry Loc"], ["31350", "PARAF MPx 6x18 ZNP TRIV 8.8"], ["31370", "PARAF MPx 6x22 ZNB triv"], ["31370.1", "PARAF MPx 6x22 ZNB triv"], ["31380", "PARAF MPx 6x25 ZNB triv+ sel"], ["31455", "PARAF (+)MFFx 5x35,5(9,9) ZNP triv 8.8 CH Corpo"], ["31455.1", "PARAF (+)MFFx 5x35,5(9,9) ZNP triv 8.8 CH Corpo"], ["31455.2", "PARAF (+)MFFx 5x35,5(9,9) ZNP triv 8.8 CH Corpo"], ["31460", "PARAF (SL) MFF 6x16 CH 10.9 decap"], ["31461", "PARAF (SL) MFF 6x16 CH 10.9 s/acab prec85"], ["31462", "PARAF (SL) MFF 7x18 decap 10.9 CH"], ["31466", "PARAF S' (SI) MFF 5x9 ZnLix triv 8.8 (QW)"], ["31467", "(SI) MT 6x14 (8) Geomet Preto (8.8) C/CORPO"], ["31475", "PARAF (SI) MP 10x32 ZnLix triv 10.9 CH"], ["31475/1", "PARAF (SI) MP 10x32 ZnLix triv 10.9 CH"], ["31476", "PARAF MFF 10-1,25x38(11) CH decap"], ["31476/1", "PARAF MFF 10-1,25x38(11) CH decap"], ["31478", "PARAF (SI) MT 10x32 (18) ZNLIX TRIV 10.9 (CH)"], ["31480", "PARAF (SI) MP 8x27 (12,5) ZNB triv 10.9 CH Corpo"], ["31480.1", "PARAF (SI) MP 8x27 (12,5) ZNB triv 10.9 CH Corpo"], ["31481", "PARAF MPW 5x12(8) ZNP triv corpo CH"], ["31481.1", "PARAF MPW 5x12(8) ZNP triv corpo CH"], ["31482", "PARAF MPx 5x14 ZNA triv + sel"], ["31483", "PARAF MPW 5x14,5(8) ZNP+ fe triv corpo 8.8"], ["31487", "PARAF MPW 5x15,5(10) ZNP Triv corpo"], ["31487/1", "PARAF MPW 5x15,5(10) ZNP Triv corpo"], ["31488", "PARAF (SI) MT 6x18(14) ZnLix triv 8.8 corpo"], ["31489", "PARAF MT 6x10 ZNP TRIV T.T."], ["31489.1", "PARAF MT 6x10 ZNP TRIV T.T."], ["31489.2", "PARAF MT 6x10 ZNP TRIV T.T."], ["31491", "PARAF (+) MT 4x12 ZNP triv 8.8"], ["31491.1", "PARAF (+) MT 4x12 ZNP triv 8.8"], ["31493", "PARAF (SI) MT 6x12 ZnLix triv 8.8"], ["31493.1", "PARAF (SI) MT 6x12 ZnLix triv 8.8"], ["31494.1", "PARAF MT 6x10 Cr 8.8"], ["31495", "PARAF (SI) MT 6x10 Cr 8.8"], ["31496", "PARAF (SI) MT 6x14 ZNB triv"], ["31496.1", "PARAF (SI) MT 6x14 ZNB triv"], ["31496.2", "PARAF (SI) MT 6x14  ZNB triv"], ["31497", "PARAF (SI) MT 6x14 ZNiB triv 8.8 c/ corpo"], ["31497.1", "PARAF (SI) MT 6x14  ZNiB triv 8.8 c/ corpo"], ["31498", "PARAF (SI) MT 6x16,5 ZNP triv 8.8"], ["31499", "PARAF (SI) MT 6x25 ZNB triv"], ["31499.1", "PARAF (SI) MT 6x25 ZNB triv"], ["31499.2", "PARAF (SI) MT 6x25 ZNB triv"], ["31499/1", "PARAF (SI) MT 6x25 ZNB triv"], ["31500", "PARAF MFx 4x12 ZNB triv+ sel  8.8"], ["31500.1", "PARAF MFx 4x12 ZNB triv+ sel  8.8"], ["31502", "PARAF MF 4x12 ZNP Triv"], ["31502.2", "PARAF MF 4x12 ZNP+fe triv"], ["31502/1", "PARAF MF 4x12 ZNP+fe triv"], ["31509", "PARAF (SI) MT 6x25 ZNP triv"], ["31534", "PARAF MF 6x12 ZNB TRIV sel Nylon  180º"], ["31535", "PARAF MFx 6x12 ZNB triv+ sel 8.8 Nylon  180º"], ["31535.1", "PARAF MFx 6x12 ZNB triv+ sel 8.8 Nylon  180º"], ["31535.2", "PARAF MFx 6x12 ZNB triv+ sel 8.8 Nylon  180º"], ["31535.5", "PARAF MFx 6x12 ZNB triv+ sel 8.8 Nylon  180º"], ["31535/1", "PARAF MFx 6x12 ZNB triv+ sel 8.8 Nylon  180º"], ["31550", "PARAF MFx 6x16 ZNB triv+ sel 8.8"], ["31570", "PARAF MFx 6x30 ZNA triv+ sel 8.8"], ["31600", "PARAF MOx 5x12 ZNB triv+ sel 8.8"], ["31600.2", "PARAF MOx 5x12 ZNB triv+ sel   8.8"], ["31610", "PARAF MOx 5x16 ZNB triv+ sel  8.8"], ["31615", "PARAF MOx 5x16 ZNP+fe triv"], ["31627", "PARAF MOx 5x18 ZNP+fe triv"], ["31627.2", "PARAF MOx 5x18 ZNP+fe triv"], ["31630", "PARAF MOx 5x20 ZNB triv+ sel"], ["31680", "PARAF MOx 6x40 ZNP triv 8.8 Nylon Patch 360º"], ["31680.2", "PARAF MOx 6x40 ZNP triv Nylon Patch  8.8"], ["31718", "PARAF S' MPx 4x8 ZNB triv (CW)(AW) 8.8 Dry Loc"], ["31718.2", "PARAF S' MPx 4x8 ZNB triv (CW)(AW) 8.8 Dry Loc"], ["31750", "PARAF S' MP 4x12 ZNA triv (CW)(AW)"], ["31750.1", "PARAF S' MP 4x12 ZnLix triv (CW)(AW)"], ["31755", "PARAF S' MPx 4x12 ZNP+fe triv (AW) 8.8"], ["31755/1", "PARAF S' MPx 4x12 ZNP+fe triv (AW) 8.8"], ["31790", "PARAF S' MPx 5x12 ZNB triv (AW) 8.8"], ["31791", "PARAF S' MPx 5x12 ZNP triv (AW) 8.8"], ["31796", "PARAF S' MP 5x14 ZNA triv + sel (AW)"], ["31796.1", "PARAF S' MP 5x14 ZNA triv + sel (AW)"], ["31796/1", "PARAF S' MP 5x14 ZNA triv + sel (AW)"], ["31796/2", "PARAF S' MP 5x14 ZNA triv + sel (AW)"], ["31799", "PARAF S' MPx 5x10 ZnLix triv (QW)(AW)"], ["31803", "PARAF S' MPx 4x16 ZNP+fe triv (CW)(AW)"], ["31806", "PARAF S' MP 5x10 ZNP+fe triv (AW)"], ["31809", "PARAF S' MPx 5x16 ZNB triv (CW)(AW)  8.8"], ["31809/1", "PARAF S' MPx 5x16  ZNB triv (CW)(AW)  8.8"], ["31810", "PARAF S' MPx 5x20 ZNB triv (CW)"], ["31811", "PARAF S' MPx 5x16 ZNP+fe triv (AW)"], ["31812", "PARAF S' MPx 5x20 ZNP+fe triv (CW) 8.8"], ["31813", "PARAF S' MPx 5x20 ZnNiP triv (QW)  8.8"], ["31813.1", "PARAF S' MPx 5x20 ZNiP triv (QW)  8.8"], ["31814", "PARAF S' MPx 5x16 ZNP+fe triv (CW)(AW)  8.8"], ["31815", "PARAF S' MPx 5x16 ZNP triv (AW-035) 8.8"], ["31816", "PARAF S' MPx 5x16 ZNP+fe triv (CW)"], ["31816.3", "PARAF S' MPx 5x16 ZNP+fe triv (CW)"], ["31816/1", "PARAF S' MPx 5x16 ZNP+fe triv (CW)"], ["31817", "PARAF S' MPx 5x25 ZNP+fe triv (AW) 8.8"], ["31817.2", "PARAF S' MPx 5x25 ZNP+fe triv (AW)  8.8"], ["31817/1", "PARAF S' MPx 5x25 ZNP+fe triv (AW)   8.8"], ["31818", "PARAF S' MPx 5x28 ZNP+fe triv (CW)"], ["31819.1", "PARAF S' MP 5x16 ZNA triv (AW)"], ["31821", "PARAF S' MPx 5x25 ZNA Triv (AW) 8.8"], ["31823", "PARAF S' MPx 5x20 ZNP TRIV 8.8 (AW)"], ["31826", "PARAF S' MPx 5x20 ZNP +Fe TRIV (QW)  8.8"], ["31828", "PARAF S' MPx 5x22 ZNLIX triv (AW) 8.8 Nylon 360"], ["31834", "PARAF S' MPx 5x45 ZNB triv (CW) 8.8"], ["31834/1", "PARAF S' MPx 5x45 ZNB triv (CW) 8.8"], ["31845", "PARAF S' MPx 5x25 ZnP+Fe  Triv (8.8)  (QW)"], ["31846", "S' MPx 5x18 ZnA Triv. (8.8)(AW)"], ["31867", "PARAF S' MUP 4x22 ZNB triv (AW) 8.8"], ["31871", "PARAF S' MUP 6x12 Decap On. 8.8  RW"], ["31872", "PARAF S' MUP 6x12 ZNA triv 8.8 (AW)"], ["31872.1", "PARAF S' MUP 6x12 ZNA triv 8.8 (AW)"], ["31873", "PARAF S' MUP 6x12 ZNA triv 8.8 (AW)"], ["31874", "PARAF S' MUP 8x16 ZnLix triv 10.9 (AW)"], ["31876", "PARAF S' MUP 6x16 ZNLIX TRIV 8.8 RW"], ["31877", "PARAF S' MUP 6 x 16 ZNLIX TRIV 8.8 AW"], ["31878", "PARAF S' MUP 6x28 ZnA triv 8.8 (AW)"], ["31879", "PARAF S' MUP 6x30 ZnLix triv 8.8 (AW)"], ["31879.1", "PARAF S' MUP 6x30 ZnLix triv 8.8 (AW)"], ["31880", "PARAF S' MUP 6x20 ZNB triv 8.8 (AW)"], ["31880/1", "PARAF S' MUP 6x20 ZNB triv 8.8 (AW)"], ["31881", "PARAF S' MUP 6x25 ZnLix triv 8.8 (AW)"], ["31883", "PARAF S' MLH 6x16 ZNB triv 8.8 (AW) Nylon Patch"], ["31885", "PARAF S' MLH 6x25 ZNP+fe triv 8.8 (AW)"], ["31888", "PARAF MUP 5x16 ZNB triv 8.8"], ["31889", "PARAF MLH 5x25(9,4) ZNB triv+sel 8.8 corpo"], ["31890", "PARAF MLH 5x26(12) ZnLix triv+sel 8.8 corpo"], ["31893", "PARAF S' MLH 5x25 ZNLIX triv 8.8 (AW)"], ["31895", "PARAF S' MLH 5x47 ZNB triv 8.8 (AW)"], ["31902", "PARAF MLH 6x45 (19) ZNLIX TRIV 8.8"], ["31904", "PARAF MLH 6x10 ZNB triv+ sel 8.8 ressalto"], ["31904.1", "PARAF MLH 6x10 ZNB triv+ sel 8.8 ressalto"], ["31904/1", "PARAF MLH 6x10 ZNB triv+ sel 8.8 ressalto"], ["31910", "PARAF MLH 8x26(13,5) ZnLix triv 8.8 CH Furo"], ["31910.1", "PARAF MLH 8x26(13,5) ZnLix triv 8.8 CH Furo"], ["31911", "PARAF MLH 8x25 ZnLix triv 8.8"], ["31912", "PARAF MLH 8x24,5(13,5) ZNA triv CH"], ["31913", "PARAF MLH 8x30,5(13,5) ZNA triv CH  8.8"], ["31913.1", "PARAF MLH 8x30,5(13,5) ZNA triv CH  8.8"], ["31915", "PARAF MUPW 10x38(19) ZNP triv Furo na cab 8.8"], ["31915.2", "PARAF MUPW 10x38(19) ZNP triv Furo na cab  8.8"], ["31916", "PARAF MUPW 8x38(22) Gp 8.8"], ["31916.1", "PARAF MUPW 8x38(22) Geo Preto 8.8"], ["31918", "PARAF MUPW 5x12(9,3) decap 10.9"], ["31920", "PARAF MUPW 6x10 ZNB triv 8.8"], ["31920.1", "PARAF MUPW 6x10 ZNB triv 8.8"], ["31921", "PARAF MUPW 6x10 ZNP triv 8.8"], ["31921.1", "PARAF MUPW 6x10 ZNP triv 8.8"], ["31922", "PARAF MUPW 6x12 ZNB triv 8.8 Nylon Patch"], ["31923", "PARAF MUPW 8x20,5(7) ZNB triv pta guia retificada"], ["31926", "PARAF MUPW 6x30 (18)ZnLix triv 8.8"], ["31929", "PARAF MUPW 8x35 (22)ZnLix triv 10.9"], ["31929.1", "PARAF MUPW 8x35 (22)ZnLix triv 10.9"], ["31929.2", "PARAF MUPW 8x35 (22)ZnLix triv 10.9"], ["31929/1", "PARAF MUPW 8x35 (22)ZnLix triv 10.9"], ["31930", "PARAF MUPW 6x16 ZnLix triv 8.8"], ["31930.2", "PARAF MUPW 6x16 ZnLix triv 8.8"], ["31931", "PARAF MUPW 6x22 (18)ZnLix triv"], ["31932", "PARAF MUPW 8x32(22) ZNP triv c/ Corpo 8.8"], ["31935", "PARAF MUPW 8x28(22) ZNB triv+sel 8.8"], ["31935/1", "PARAF MUPW 8x28(22) ZNB triv+sel 8.8"], ["31936", "PARAF MUPWRO 6x16 ZNP triv 8.8"], ["31937", "PARAF MUPWRO 6x14 ZNP triv 8.8"], ["31939", "PARAF MUPWRO 6x12 ZNB triv 8.8"], ["31939.2", "PARAF MUPWRO 6x12 ZNB triv 8.8"], ["31940", "PARAF MUPWRO 6x85(18) ZnLix triv 8.8"], ["31941", "PARAF MUPWR 8x40(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31941.2", "PARAF MUPWR 8x40(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31941.3", "PARAF MUPWR 8x40(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31941.4", "PARAF MUPWR 8x40(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31941/1", "PARAF MUPWR 8x40(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31942", "PARAF MUPWR 8x50(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31942.2", "PARAF MUPWR 8x50(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31942.4", "PARAF MUPWR 8x50(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31942.5", "PARAF MUPWR 8x50(18) ZNB triv+SEL 10.9 Nylon Patch"], ["31943", "PARAF MUPWR 8x40(15) ZNB triv+SEL 10.9"], ["31943.1", "PARAF MUPWR 8x40(15) ZNB triv+SEL 10.9"], ["31944", "PARAF MUPWRO 6x10 Cr 8.8"], ["31946", "PARAF MUPW 8x50(22) ZnLix triv+SEL c/ Corpo 8.8"], ["31946.2", "PARAF MUPW 8x50(22) ZnLix triv+SEL c/ Corpo 8.8"], ["31947", "PARAF MUPW 8x50(22) ZNB triv+SEL 8.8"], ["31947.2", "PARAF MUPW 8x50(22) ZNB triv+SEL 8.8"], ["31947/1", "PARAF MUPW 8x50(22) ZNB triv+SEL 8.8"], ["31949", "PARAF MUPW 8x70(22) ZNB triv+SEL 8.8"], ["31950", "PARAF (+) MUPWR 4x10,5 (4,2) ZNP triv corpo 8.8"], ["31950.1", "PARAF (+) MUPWR 4x10,5 (4,2) ZNP triv corpo 8.8"], ["31951", "PARAF MUPWR 6x14(10) ZNB triv+SEL 8.8 corpo"], ["31952", "PARAF MUPWR 6x12(8) ZnLix triv+SEL 8.8 corpo"], ["31953", "PARAF MUPWR 6x18,5(8) ZnLix+sel 8.8 corpo"], ["31953/1", "PARAF MUPWR 6X18,5 (8,5) ZNLIX TRIV+SEL (8.8)"], ["31954", "PARAF MUPWR 6x17(10,7) ZNB triv+SEL 8.8 corpo"], ["31954.2", "PARAF MUPWR 6x17(10,7) ZNB triv+SEL 8.8 corpo"], ["31954.3", "PARAF MUPWR 6x17(10,7) ZNB triv+SEL 8.8 corpo"], ["31954/1", "PARAF MUPWR 6x17(10,7) ZNB triv+SEL 8.8 corpo"], ["31955", "PARAF MUPW 6x18 ZNA triv 8.8"], ["31956", "PARAF MUPW 6x22 ZNB triv 8.8"], ["31957", "PARAF MUPWRO 6x16 ZnLix triv 8.8"], ["31958", "PARAF MUPWRO 6x20 ZNB triv 8.8"], ["31958.1", "PARAF MUPWRO 6x20 ZNB triv 8.8"], ["31959", "PARAF MUPWRO 6x75(18) ZNB triv8.8"], ["31960", "PARAF MUPWRO 6x25(18) ZNB triv8.8"], ["31960.1", "PARAF MUPWRO 6x25(18) ZNB triv8.8"], ["31962", "PARAF MUPW 6x20 ZnLix triv 10.9"], ["31963", "PARAF MUPW 6x20 ZNP triv 8.8"], ["31964", "PARAF MUPW 6x28(18) ZnLix  8.8"], ["31965", "PARAF MUPW 6x25 (18) ZNB triv 8.8"], ["31965.1", "PARAF MUPW 6x25 (18) ZNB triv 8.8"], ["31965.2", "PARAF MUPW 6x25 (18) ZNB triv 8.8"], ["31966", "PARAF MUPW 6x35 ZNB triv 8.8"], ["31966.1", "PARAF MUPW 6x35 ZNLIX triv 8.8"], ["31968", "PARAF MUPW 6x45 ZnLiX 8.8"], ["31970", "PARAF MUPWRO 6x14(10) ZNP+fe triv 8.8"], ["31970/1", "PARAF MUPWRO 6x14(10) ZNP+fe triv 8.8"], ["31971", "PARAF MUPWRO 6x40(18) ZnLix triv 8.8"], ["31972", "PARAF MUPWRO 6x60(18) ZnLix triv 8.8"], ["31974", "PARAF MUPWR 6x15,5(9,2) ZNA triv+SEL 8.8 corpo"], ["31974/4", "PARAF MUPWR 6x15,5(9,2) ZNA triv+SEL 8.8 corpo"], ["31976", "PARAF MUPWR 6x18(14) ZNB triv+SEL 8.8 corpo"], ["31976.1", "PARAF MUPWR 6x18(14) ZNB triv+SEL 8.8 corpo"], ["31976.2", "PARAF MUPWR 6x18(14) ZNB triv+SEL 8.8 corpo"], ["31978", "PARAF MUPW 6x92,5(12) ZnLix 8.8 c/ corpo"], ["31978.1", "PARAF MUPW 6x92,5(12) ZnLix 8.8 c/ corpo"], ["31979", "PARAF MUPW 6x70(18) ZNB triv+SEL 8.8"], ["31979.1", "PARAF MUPW 6x70(18) ZNB triv+SEL 8.8"], ["31981", "PARAF MUPW 8x14 ZNB triv+ SEL 8.8"], ["31981.2", "PARAF MUPW 8x14 ZNB triv+ SEL 8.8"], ["31981.4", "PARAF MUPW 8x14 ZNA triv+ SEL 8.8"], ["31982", "PARAF MUPW 6x120 Decap 10.9"], ["31982.1", "PARAF MUPW 6x120 Decap 10.9"], ["31983", "PARAF MUPW 6x65 (18) ZNB triv 8.8"], ["31985", "PARAF MUPW 6x95(18) ZnLix triv 8.8"], ["31988", "PARAF MUPW 8x18 ZNB triv 8.8"], ["31989", "PARAF MUPW 8x18 ZNP triv 8.8"], ["31989.2", "PARAF MUPW 8x18 ZNP triv 8.8"], ["31991", "PARAF MUPW 8x85(22) ZnLix triv 8.8 CH Corpo"], ["31994", "PARAF MUPW 8x20 ZNP triv 8.8"], ["31996", "PARAF MUPW 8x45(22) ZnLix triv  10.9"], ["31996.1", "PARAF MUPW 8x45(22) ZnLix triv  10.9"], ["31996.2", "PARAF MUPW 8x45(22) ZnLix triv  10.9"], ["31996.3", "PARAF MUPW 8x45(22) ZnLix triv  10.9"], ["31997", "PARAF MUPW 8x38(22) ZnLix triv  8.8"], ["31998", "PARAF MUPW 8x75 ZnLix triv 8.8"], ["31998.1", "PARAF MUPW 8x75 ZnLix triv 8.8"], ["32001", "PARAF MUPW 10-1,25x45(26) ZnLix triv 10.9 c/ Corpo"], ["32003", "PARAF MUPW 10-1,25x50(26) ZnLix triv 10.9 c/ Corpo"], ["32003.1", "PARAF MUPW 10-1,25x50(26) ZnLix triv 10.9 c/ Corpo"], ["32003.2", "PARAF MUPW 10-1,25x50(26) ZnLix triv 10.9 c/ Corpo"], ["32005", "PARAF MUPW 10x65(26) ZnLix triv 8.8 Corpo"], ["32009", "PARAF MUPW 10-1,25x40(26) ZnLix triv 8.8"], ["32010", "PARAF MUPW 10x45(26) ZNB triv 8.8"], ["32010.1", "PARAF MUPW 10x45(26) ZNB triv 8.8"], ["32011", "PARAF MUPW 10-1,25x50(26) ZnLix triv 8.8 c/ Corpo"], ["32011.1", "PARAF MUPW 10-1,25x50(26) ZnLix triv 8.8 c/ Corpo"], ["32011.2", "PARAF MUPW 10-1,25x50(26) ZnLix triv 8.8 c/ Corpo"], ["32012", "PARAF MUPW 10-1,25x25 ZnLix triv 8.8 c/ Corpo"], ["32015", "PARAF MUPW 10-1,25x105 (26) ZnLix triv 8.8  CH"], ["32018", "PARAF MUPWR 10x52(15) ZNB triv 10.9 CH Nylon"], ["32035", "PARAF MUPW 6x45(18) DECAP (8.8)"], ["32040", "PARAF MUPW 6x80(18) ZnLix triv (8.8)"], ["32040.1", "PARAF MUPW 6x80(18) ZnLix triv (8.8)"], ["32049", "PARAF MUPW 6x22(18) ZnLix triv (8.8)"], ["32049.1", "PARAF MUPW 6x22(18) ZnLix triv (8.8)"], ["32056", "PARAF MUPW 6x18 ZNLix TRIV + SEL01 8.8"], ["32058", "PARAF (+) MUPWx 5x8 ZnLix triv 8.8"], ["32062", "MUPWR 6X12 ZnNiA(8.8)(Ch) (Tork Break)(Nylon Patch)"], ["32072", "PARAF MUPWR 6x14 ZnLix Triv 8.8 corpo"], ["32075", "PARAF MUPWR 6x16(12) ZNB triv+SEL 8.8 corpo"], ["32075/1", "PARAF MUPWR 6x16(12) ZNB triv+SEL 8.8 corpo"], ["32080", "MUPWO 6x16 ZnA Triv.(8.8) (C/CorpoØ10)"], ["32105", "PARAF Prisioneiro MUP (M8 x14)x(8x23,5)x41 Decap"], ["32110", "PARAF Prisioneiro M 8x38 ZNB triv 10.9"], ["32410", "PARAF(SI) MTx 6x8 CROMADO (8.8)"], ["32410.1", "PARAF(SI) MTx 6x8 CROMADO (8.8)"], ["32418", "PARAF (SI) MT 6x14(8) ZNP triv 8.8 Corpo"], ["32418.1", "PARAF (SI) MT 6x14(8) ZNP triv 8.8 Corpo"], ["32422", "PARAF (SI) MT 6x14(8) ZNB triv 8.8 Corpo"], ["32450", "PARAF MPWx 5x14 ZNA Triv 8.8"], ["32460", "PARAF (+/-) MTx 6x16(12) CROMADO 8.8 (CORPO Ø10)"], ["32600", "PARAF (SI) MFFx 6x22 (18) ZNB TRIV 8.8 Recart"], ["32650", "(SI) MFFx 8x28(22) ZnA Triv. (8.8)"], ["32650.1", "(SI) MFFx 8x28 (22) ZnA Triv. (8.8)"], ["32655", "(SI) MFFx 8x32(22) ZnA Triv. (8.8)"], ["32903", "PARAF MUPWRO 6x14 ZnLix triv 8.8"], ["32903.3", "PARAF MUPWRO 6x14 ZnLix triv 8.8"], ["32904", "PARAF MUPWRO 6x14 ZnP triv 8.8"], ["32905", "PARAF MUPWRO 6x16 ZnLix triv 8.8"], ["32907", "PARAF MUPWRO 6x18 ZnLix triv 8.8"], ["32908", "PARAF MUPWRO 6x20(18) G 8.8"], ["32912", "PARAF MUPWRO 6x28(18) ZnLix triv 8.8"], ["32921", "PARAF MUPWRO 6x100(18) ZnLix triv 8.8"], ["32936", "PARAF MLHWRO 8x35 Cr 8.8 CH"], ["32940", "PARAF MUPWR 6x16(9) ZNP +fe triv 8.8 Nylon"], ["32941", "PARAF MUPW 8x50(22) Decap. On  8.8"], ["32942", "PARAF MUPW 8x50(22) ZNP triv+SEL 8.8"], ["32943", "PARAF MUPWR 5x12 Decap O.N 8.8 CH"], ["32947", "PARAF MUPWR 6X14(10) ZNP Triv 8.8 (CORPO Ø12)"], ["32950", "PARAF MUPWR 6x14(8) ZNB triv+SEL 8.8 corpo"], ["32951", "PARAF MUPWR 6x14(9) ZNP triv 8.8 corpo"], ["32951.2", "PARAF MUPWR 6x14(9) ZNP triv 8.8 corpo"], ["32953", "PARAF MUPWR 6x16(10,5) ZnB triv+SEL 8.8 corpo"], ["32953.1", "PARAF MUPWR 6x16(10,5) ZnA triv+SEL 8.8 corpo"], ["32953.2", "PARAF MUPWR 6x16(10,5) ZnA triv+SEL 8.8 corpo"], ["32956", "PARAF MUPWR 6x17(11,4) Znp Triv (8.8) (CORPO)"], ["32956.1", "PARAF MUPWR 6x17(11,4) Znp Triv (8.8) (CORPO)"], ["32956.2", "PARAF MUPWR 6x17(11,4) Znp Triv (8.8) (CORPO)"], ["33401", "PARAF (SL)(PT) PP1DP 2X6,8 ZN LIX TRIV"], ["33449", "PARAF (SL)(BT) BP 2,6x6 ZNB triv"], ["33450", "PARAF (SL)(BT) BP 2,6x7,5 ZNB triv"], ["33451", "PARAF (SL)(BT) BP 2,6x8 ZNB triv esp"], ["33503", "PARAF (SL)(BT) BP 3x6 ZNB triv"], ["34800", "PARAF (SL) KNPW 4x14 ZNLIX triv 10.9 cab.maior"], ["34850", "PARAF (SL) KNPW 5x20 Gp 10.9 Pta.Redonda"], ["35011", "PARAF (SL) THN1P 3x10 Pl 10.9"], ["35012", "PARAF (SL)THN1P 3x10 ZnLix Triv (10.9)"], ["35013", "PARAF (SL)THN1P 3x10 Zinklad (10.9)"], ["35015", "PARAF (SL) THN1P 3x10 ZNB triv 10.9"], ["35071", "PARAF (SL) THN2P 4,2x40 ZNiP triv"], ["35921", "PARAF (+)THN1UPW #10-16x 30 Gp"], ["36005", "PARAF (PZ) THN2PW 4,2x13 Gp"], ["36120", "PARAF PNP 3,5x12 ZNA Triv SAE 1018"], ["36610", "PNP 4x16 Geo Preto + Plus (V)"], ["36681", "PARAF (+-) PNP 4x65(15) ZNB triv 8.8"], ["36881", "PARAF (SL) PNPW 4x8 ZNB Triv"], ["36950", "PARAF (SL) PN2PW 5x15 ZnNiP TRIV"], ["36980", "PARAF MUPWR 8x25(15) ZNB triv+SEL 9.8"], ["36990", "PARAF PNUPW 4,2x16 ZNB triv"], ["37150", "PARAF (SL) KP 3,5x14 ZNA triv"], ["37151", "PARAF (SL) KP 3,5x14 Zin Nip  Triv."], ["37316", "PARAF (+-) KFF 3,5x18 ZNB triv (V)"], ["37317", "PARAF (+-) KFF 3,5x18 ZNP + FE TRIV 8.8 C/ CORPO"], ["37403", "PARAF (SL) KPW 3x6 ZinKlad 10.9"], ["37406", "PARAF (SL) KPW 3x10 ZNB triv10.9 ch"], ["37502", "PARAF KPW 4x10 ZNP TRIV"], ["37517", "PARAF (SL) KPW 5x20 ZNNIP"], ["37755", "PARAF KTW 4x8 ZNP Triv"], ["38105", "PARAF (LT) BP 4x10 ZNA triv+SEL"], ["38391", "PARAF (LT) BT 4x10 ZNP+fe triv"], ["38428", "PARAF (LT) BT 4x10 ZNA triv+SEL"], ["38428/1", "PARAF (LT) BT 4x10 ZNA triv+SEL"], ["38430", "PARAF (LT) BT 4x12 ZNA triv+SEL"], ["38430.2", "PARAF (LT) BT 4x12 ZNA triv+SEL"], ["38430.4", "PARAF (LT) BT 4x12 ZNA triv+SEL"], ["38461", "PARAF (LT) BT 5x16 ZNB triv+SEL"], ["38461.4", "PARAF (LT) BT 5x16 ZNB triv+SEL"], ["38461.7", "PARAF (LT) BT 5x16 ZNB triv+SEL"], ["38461.9", "PARAF (LT) BT 5x16 ZNB triv+SEL"], ["38461/1", "PARAF (LT) BT 5x16 ZNB triv+SEL"], ["38461/2", "PARAF (LT) BT 5x16 ZNB triv+SEL"], ["38600", "PARAF ABT 4X12 ZNP TRIV"], ["38696", "PARAF (LT) ABT 4x10 ZNA triv+SEL"], ["38696.2", "PARAF (LT) ABT 4x10 ZNA triv+SEL"], ["38730", "PARAF (LT) BT 5x14 ZNB triv"], ["38730.4", "PARAF (LT) BT 5x14 ZNB triv"], ["38730.6", "PARAF (LT) BT 5x14 ZNB triv"], ["39201", "PARAF (PST) ABV 3,2x25 ZNA triv"], ["41310", "PARAF MUPW 5x14 Ox.CH 8.8"], ["41315", "PARAF MUPW 5x25 ZnB Triv 8.8"], ["41470", "PARAF MUPW 6x90 (18) ZnB triv 8.8"], ["41490", "PARAF MUPW 6x105 (20) Oleado 10.9 c/ Corpo"], ["41495", "PARAF MUPW 6x130 (20) Znb Triv. 10.9 c/ Corpo"], ["41500", "PARAF MUPWR 6x28 (18) ZnB triv 8.8 Reb.Abau"], ["41520", "PARAF MUPWR 6x45 (18) ZnB triv 8.8 Reb.Abau"], ["41540", "PARAF MUPWR 6x65 (18) ZnB triv 8.8 Reb.Abau"], ["41550", "PARAF MUPWR 6x80 (18) ZnB triv 8.8 Reb.Abau"], ["41570", "PARAF MLHWR 6x130 (18) ZnB triv 8.8 Reb.Abau"], ["41610", "PARAF MUPWRO 6X39,5(15) ZnB TRIV (8.8) (CH)"], ["41620", "PARAF MUPWRO 6X45(18) ZNB Triv (8.8) (FLANGE Ø13)"], ["41700", "PARAF MUPW 8x18 ZNP Triv 8.8 Nylon"], ["41931", "PARAF MUPW 8x14 ZnP Triv 8.8"], ["41932", "PARAF MUPW 8x20(13,5) ZnB Triv 8.8 (Corpo Ø12,7)"], ["41933", "PARAF MUPW 8x16 ZNA triv 8.8"], ["41933.1", "PARAF MUPW 8 x 16 ZNA triv 8.8"], ["41934", "PARAF MUPW 8x16 ZnLix triv 8.8"], ["41934.1", "PARAF MUPW 8x16 ZnLix triv 8.8"], ["41944", "PARAF MUPW 8x20 ZNA triv 10.9"], ["41945", "PARAF MUPW 8x28(22) ZN LIX TRIV 8.8 CH"], ["42018", "PARAF MUPW 10x150(26) ZnLix 8.8 CH"], ["50999", "PARAF (LTRE) BPW 4X12 Znb Triv"], ["51010", "(LTRE) BPW 5X16 ZnB Triv"], ["51264", "Bucha Ø12x6,4 ZnA Triv. (FlangeØ20,2)(FuroØ8,2)"], ["51413", "Bucha Ø14,1x3 ZnA Triv. (FlangeØ19)(FuroØ8)"], ["51500", "Bucha Ø12,7x7 ZnA Triv. (c flange Ø20)(furo Ø8,5)"], ["51500/1", "Bucha Ø12,7x9 ZnA Triv. (c flange Ø20)(furo Ø8,5)"], ["51600", "Bucha 9,5x7,5 ZnB Triv. (c flange Ø18)(furo Ø6,3)"], ["51600.1", "Bucha 9,5x7,5 ZnB Triv. (c flange Ø18)(furo Ø6,3)"], ["51620", "BUCHA Ø9,2X21,5 ZNB TRIV. (FLANGE Ø16)(FURO Ø6,2)"], ["51620.1", "BUCHA Ø9,2X21,5 ZNB TRIV. (FLANGE Ø16)(FURO Ø6,2)"], ["60100", "Bucha Cega Ø10x16 Decap O.N. (Furo Roscado)"], ["60100/1", "Bucha Cega Ø10x16 Decap O.N. (Furo Roscado)"], ["61028", "ARRUELA PLANA 16,30x21,90 X1,50"], ["61040", "PORCA SEXTAVADA c/ FLANGE M12x1,25"], ["61084", "ARRUELA PRESSAO M6"], ["61612", "Arruela Plana M6x12,5 (Ø6,5) ZnA Triv"], ["61817", "Arruela Plana M8x17(Ø8,5) ZnA Triv"], ["61821", "Arruela Plana M8x21(Ø8,5) ZnA Triv"], ["95000", "ABRACADEIRA METALICA Ø48,3 PINTURA PRETA"], ["CW-082", "ARR. PRESSAO 3,55x7,00x 1,00 COD/REV CW-AAA/3"]];
const CPD_MAP = {};
CPD_DATA.forEach(([c,d])=>CPD_MAP[c]=d);
let manualCPD = {}; // sincronizado com a coleção cpdManual do Firestore (compartilhado com o time)

const SETORES = ["Prensa","Rosca","USF","Usinagem","Recortador","Fresa","Forno","V/ TÉRMICO","MTC - TT","Éden","V/ SUPERFICIAL","MTC - TS","Sipra","Martins","Multstamp","Realtec","Indusmek","Nylok","Mogi","Aguardando retorno","Aguardando escolha","Concluído","Cancelado","Outro"];

const CLIENTES = ["HONDA","NISSAN TRADING","JOTAEME","COMPONEL","YASUFUKU","HITACHI ASTEMO","METALFINO","MINEBEA MITSUMI","MITSUBA","HI-LEX","WEG","DENSO","MAKITA","CAVERNA","PORÃO MOTOS BORACEIA","SCORPIOS INDÚSTRIA METALÚ","SMRC","VISTEON","JOYSON","BELLS INDÚSTRIA E COMERCI","MAHLE","APTIV","NEO PWT","INTEF","PHINIA","PLASTICOMP INDÚSTRIA E CO","SAKAGUCHI"];

const HONDA_GROUP = ["HONDA","METALFINO","YASUFUKU"];

const STATUS_CFG = {
  pendente:{label:'Pendente',border:'var(--amber-border)',bg:'var(--amber-bg)',col:'var(--amber)'},
  termico:{label:'V/ TÉRMICO',border:'var(--blue-border)',bg:'var(--blue-bg)',col:'var(--blue)'},
  superficial:{label:'V/ SUPERFICIAL',border:'var(--purple-border)',bg:'var(--purple-bg)',col:'var(--purple)'},
  retorno:{label:'Aguardando retorno',border:'var(--purple-border)',bg:'var(--purple-bg)',col:'var(--purple)'},
  escolha:{label:'Aguardando escolha',border:'var(--amber-border)',bg:'var(--amber-bg)',col:'var(--amber)'},
  concluido:{label:'Concluído',border:'var(--green-border)',bg:'var(--green-bg)',col:'var(--green)'},
  cancelado:{label:'Cancelado',border:'var(--red-border)',bg:'var(--red-bg)',col:'var(--red)'},
};
function normalizeStatusLabel(v){
  v = String(v || '').trim();
  if(!v) return 'Pendente';
  const mapa = {
    'pendente':'Pendente',
    'v/ térmico':'V/ TÉRMICO','v/ termico':'V/ TÉRMICO','térmico':'V/ TÉRMICO','termico':'V/ TÉRMICO',
    'v/ superficial':'V/ SUPERFICIAL','superficial':'V/ SUPERFICIAL',
    'aguardando retorno':'Aguardando retorno',
    'aguardando escolha':'Aguardando escolha',
    'concluido':'Concluído','concluído':'Concluído','escolha':'Concluído',
    'cancelado':'Cancelado','cancelada':'Cancelado'
  };
  return mapa[v.toLowerCase()] || v;
}
function computeStatus(o){
  const st = normalizeStatusLabel(o.setor || o.status || 'Pendente');
  if(st === 'Concluído') return 'concluido';
  if(st === 'Cancelado') return 'cancelado';
  if(st === 'V/ TÉRMICO') return 'termico';
  if(st === 'V/ SUPERFICIAL') return 'superficial';
  if(st === 'Aguardando retorno') return 'retorno';
  if(st === 'Aguardando escolha') return 'escolha';
  return 'pendente';
}
function isFinalizado(o){ return ['concluido','cancelado'].includes(computeStatus(o)); }
function statusLabel(o){ return STATUS_CFG[computeStatus(o)]?.label || 'Pendente'; }
function normalizaTexto(v){
  return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
}
function setorRank(o){
  const s = normalizaTexto(o.setor || '');
  if(s === 'prensa') return 0;
  if(s === 'rosca') return 1;
  if(['usinagem','usf','recortador','fresa'].includes(s)) return 2;
  if(s === 'forno') return 3;
  if(['v/ termico','termico','mtc - tt','mtc-tt','eden'].includes(s)) return 4;
  if(['v/ superficial','superficial','mtc - ts','mtc-ts','sipra','martins','multstamp','realtec','indusmek','mogi'].includes(s)) return 5;
  if(s === 'nylok') return 6;
  if(s === 'aguardando escolha') return 7;
  if(s === 'aguardando retorno') return 8;
  return 9;
}
function setorGrupoUrgencia(o){
  const s = normalizaTexto(o.setor || '');
  if(['prensa','rosca','usinagem','usf','recortador','fresa'].includes(s)) return 'interno';
  if(['forno','v/ termico','termico','mtc - tt','mtc-tt','eden'].includes(s)) return 'termico';
  if(['v/ superficial','superficial','mtc - ts','mtc-ts','sipra','martins','multstamp','realtec','indusmek','mogi'].includes(s)) return 'superficial';
  if(s === 'nylok') return 'nylok';
  if(s === 'aguardando escolha') return 'escolha';
  return 'outro';
}
function startOfWeek(d){
  const x = new Date(d); x.setHours(0,0,0,0);
  const day = x.getDay(); const diff = (day + 6) % 7;
  x.setDate(x.getDate() - diff);
  return x;
}
function semanaOffset(dataIso){
  if(!dataIso) return 99;
  const due = new Date(dataIso+'T00:00:00');
  if(isNaN(due.getTime())) return 99;
  const now = new Date(); now.setHours(0,0,0,0);
  const a = startOfWeek(now); const b = startOfWeek(due);
  return Math.round((b-a)/604800000);
}
function urgencyInfo(o){
  if(isFinalizado(o)) return {cls:'', label:''};
  const off = semanaOffset(o.dataEntregaAtual);
  const grupo = setorGrupoUrgencia(o);
  const setor = normalizaTexto(o.setor || '');
  if(off <= 1){
    if(grupo === 'interno') return {cls:'risk-high', label:'URGENTE - processo inicial'};
    if(grupo === 'termico') return {cls:'risk-mid', label:'ATENÇÃO - forno/térmico'};
    if(grupo === 'superficial') return {cls:'risk-low', label:'MONITORAR - superficial/externo'};
    if(grupo === 'nylok') return {cls:'risk-nylok', label:'NYLOK - trava'};
  }
  if(off === 2){
    if(grupo === 'interno') return {cls:'risk-high', label:'ANTECIPAR - processo inicial'};
    if(grupo === 'termico') return {cls:'risk-mid', label:'PROGRAMAR - forno/térmico'};
  }
  if(off === 3 && ['prensa','rosca'].includes(setor)){
    return {cls:'risk-high', label:'ANTECIPAR - prensa/rosca'};
  }
  return {cls:'', label:''};
}
function atrasoDiasPedido(o){
  if(!o.dataEntregaAtual) return -999999;
  const d=new Date(o.dataEntregaAtual+'T00:00:00');
  const t=new Date(); t.setHours(0,0,0,0);
  return Math.round((t-d)/86400000);
}
function compareAtrasoProcesso(a,b){
  const da = atrasoDiasPedido(a), db = atrasoDiasPedido(b);
  if(db !== da) return db - da;
  const ra = setorRank(a), rb = setorRank(b);
  if(ra !== rb) return ra - rb;
  return String(a.dataEntregaAtual||'').localeCompare(String(b.dataEntregaAtual||'')) || String(a.cpd||'').localeCompare(String(b.cpd||''));
}
function renderAttentionPanel(){
  const el = document.getElementById('attention-panel');
  if(!el) return;
  el.style.display = 'none';
  el.innerHTML = '';
}
function renderNotas(){
  const panel = document.getElementById('notes-panel'); if(!panel) return;
  const ativos = orders.filter(o=>!isFinalizado(o));
  const vencidos = ativos.filter(o=>atrasoDiasPedido(o)>0).sort(compareAtrasoProcesso);
  const semanaProx = ativos.filter(o=>semanaOffset(o.dataEntregaAtual)<=1 && urgencyInfo(o).cls).sort(compareAtrasoProcesso);
  const riscoAlto = ativos.filter(o=>urgencyInfo(o).cls==='risk-high').length;
  const finalizadosHoje = orders.filter(o=>isFinalizado(o) && o.dataConclusao===todayStr()).length;

  function notaClasse(o){
    const cls = urgencyInfo(o).cls || '';
    if(cls==='risk-high') return 'high';
    if(cls==='risk-mid') return 'mid';
    if(cls==='risk-low') return 'low';
    if(cls==='risk-nylok') return 'nylok';
    return '';
  }
  function notaLabel(o){
    const info = urgencyInfo(o);
    if(info && info.label) return info.label;
    const atraso = atrasoDiasPedido(o);
    if(atraso > 0) return atraso + ' dia(s) atraso';
    const sem = semanaOffset(o.dataEntregaAtual);
    return sem <= 0 ? 'vence nesta semana' : 'semana +' + sem;
  }
  function lista(arr, vazio){
    if(!arr.length) return `<div class="notes-empty">${vazio}</div>`;
    return arr.slice(0,14).map(o=>{
      const c = notaClasse(o);
      const atraso = atrasoDiasPedido(o);
      const badgeClass = c || (atraso>0 ? 'high' : 'mid');
      return `<div class="notes-item ${c}">
        <div>
          <strong>${o.cpd}</strong>
          <div class="desc">${o.descricao || '(sem descrição)'}</div>
          <div class="meta">
            <span><b>Setor/Situação:</b> ${o.setor || '—'}${o.setorOutro ? ' - '+o.setorOutro : ''}</span>
            <span><b>Cliente:</b> ${o.cliente || '—'}</span>
            <span><b>Entrega:</b> ${fmtDate(o.dataEntregaAtual)}</span>
          </div>
        </div>
        <span class="notes-badge ${badgeClass}">${notaLabel(o)}</span>
      </div>`;
    }).join('');
  }

  panel.innerHTML = `<div class="notes-dashboard">
    <div class="notes-hero">
      <h2>Painel de atenção do PCP</h2>
      <p>Visão automática para reunião e acompanhamento diário. A fila considera atraso, semana de entrega e a ordem de processo definida pelo PCP: Prensa, Rosca, Usinagem/USF/Fresa, Forno, V/ TÉRMICO, Éden, V/ SUPERFICIAL, Mogi e Aguardando escolha.</p>
      <div class="process-flow">
        <span class="process-pill">Prensa</span><span class="process-pill">Rosca</span><span class="process-pill">USF / Usinagem</span><span class="process-pill">Recortador</span><span class="process-pill">Fresa</span><span class="process-pill">Forno / V/ TÉRMICO</span><span class="process-pill">V/ SUPERFICIAL</span><span class="process-pill">Nylok</span><span class="process-pill">Aguardando escolha</span>
      </div>
    </div>

    <div class="notes-cards">
      <div class="notes-card"><div class="num" style="color:var(--red)">${vencidos.length}</div><div class="lbl">Pedidos vencidos</div></div>
      <div class="notes-card"><div class="num" style="color:var(--amber)">${semanaProx.length}</div><div class="lbl">Próxima semana com destaque</div></div>
      <div class="notes-card"><div class="num" style="color:var(--green)">${finalizadosHoje}</div><div class="lbl">Concluídos hoje</div></div>
    </div>

    <div class="notes-section">
      <h3>🔥 Mais atrasados - ordem PCP</h3>
      <div class="notes-list">${lista(vencidos,'Nenhum pedido atrasado no momento.')}</div>
    </div>

    <div class="notes-section">
      <h3>⚠️ Próxima semana com destaque</h3>
      <div class="notes-list">${lista(semanaProx,'Nenhum item crítico para a próxima semana.')}</div>
    </div>
  </div>`;
}



/* ===================== ESTADO ===================== */
let sections = [];
let orders = [];
let currentTab = 'ativa';
let sectionFilter = 'todas';
let expandedHist = new Set();
let backendAtivo = false; // true quando o servidor SQLite está funcionando


/* ===================== BANCO COMPARTILHADO (SQLite no servidor) ===================== */
let syncVersion = 0;
let ultimaAtualizacaoBanco = '';
let carregandoBanco = false;

function setConnStatus(state, msg){
  const el = document.getElementById('conn-status');
  el.className = 'conn-status conn-'+state;
  el.textContent = '● '+msg;
}

function limparParaArray(v){ return Array.isArray(v) ? v : []; }
function limparParaObjeto(v){ return v && typeof v === 'object' && !Array.isArray(v) ? v : {}; }


const USER_KEY = 'pcp_usuario_nome_v1';
const AUTH_KEY = 'pcp_auth_v2';
let currentUserName = '';
let authInfo = null;

function isEditor(){ return authInfo && authInfo.role === 'edit'; }
function isAuthenticated(){ return !!(authInfo && authInfo.token); }

function atualizarUsuarioTela(){
  const el = document.getElementById('usuario-btn');
  if(el) el.textContent = 'Usuário: ' + (currentUserName || '—');
  document.body.classList.toggle('view-only', !isEditor());
  const note = document.getElementById('readonly-note');
  if(note) note.style.display = isEditor() ? 'none' : 'block';
  if(!isEditor() && (currentTab==='kpi' || currentTab==='anotacoes' || currentTab==='lixeira')){ currentTab='ativa'; }
}

function getCurrentUser(){
  if(!isEditor()) return authInfo ? authInfo.login : 'Visualização';
  let nome = currentUserName || (window.localStorage ? window.localStorage.getItem(USER_KEY) : '') || '';
  nome = String(nome || '').trim();
  while(!nome){
    const digitado = prompt('Digite seu nome para registrar inclusões e alterações:', '');
    if(digitado === null){
      alert('Para editar, informe o nome do usuário. Isso evita alteração sem identificação.');
      continue;
    }
    nome = String(digitado || '').trim();
    if(!nome) alert('O nome é obrigatório para registrar quem adicionou ou alterou informações.');
  }
  currentUserName = nome.slice(0, 80);
  try{ window.localStorage.setItem(USER_KEY, currentUserName); }catch(e){}
  atualizarUsuarioTela();
  return currentUserName;
}

function trocarUsuario(){
  if(!isEditor()) return;
  try{ window.localStorage.removeItem(USER_KEY); }catch(e){}
  currentUserName = '';
  getCurrentUser();
}

function sairSistema(){
  try{ window.localStorage.removeItem(AUTH_KEY); }catch(e){}
  authInfo = null;
  location.reload();
}

function normalizarLoginLocal(valor){
  let txt = String(valor || '').trim().toUpperCase();
  try{ txt = txt.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }catch(e){}
  txt = txt.replace(/[\s\-_]/g, '');
  if(txt === 'VENDA' || txt === 'COMERCIAL') return 'VENDAS';
  if(txt === 'EXP' || txt === 'EXPEDICAO') return 'EXPEDICAO';
  if(txt === 'PCP') return 'PCP';
  if(txt === 'VENDAS') return 'VENDAS';
  return txt;
}

function realizarLogin(){
  const digitado = String(document.getElementById('login-user').value || '').trim();
  const login = normalizarLoginLocal(digitado);
  const erro = document.getElementById('login-error');
  if(erro) erro.textContent = '';
  if(!login){ if(erro) erro.textContent = 'Informe o usuário.'; return; }
  const roles = { VENDAS:'view', EXPEDICAO:'view', PCP:'edit' };
  if(!roles[login]){
    if(erro) erro.textContent = 'Usuário inválido. Use VENDAS, EXPEDICAO ou PCP.';
    return;
  }
  authInfo = {login: login, role: roles[login], token: 'sem-senha'};
  try{ window.localStorage.setItem(AUTH_KEY, JSON.stringify(authInfo)); }catch(e){}
  document.getElementById('login-overlay').style.display = 'none';
  if(isEditor()) getCurrentUser(); else atualizarUsuarioTela();
  initBackend();
}

function carregarAuthSalvo(){
  try{
    const raw = window.localStorage ? window.localStorage.getItem(AUTH_KEY) : null;
    if(raw){ authInfo = JSON.parse(raw); }
  }catch(e){ authInfo = null; }
  if(authInfo && authInfo.token){
    const overlay = document.getElementById('login-overlay');
    if(overlay) overlay.style.display = 'none';
    if(isEditor()) getCurrentUser(); else atualizarUsuarioTela();
    return true;
  }
  setTimeout(()=>{ const el=document.getElementById('login-user'); if(el) el.focus(); }, 50);
  atualizarUsuarioTela();
  return false;
}

function exigirEdicao(){
  if(isEditor()) return true;
  alert('Este usuário tem acesso somente para visualização. Entre como PCP para editar.');
  return false;
}

function authHeaders(extra){
  const base = {
    'X-PCP-Login': authInfo ? authInfo.login : '',
    'X-PCP-Token': authInfo ? authInfo.token : ''
  };
  if(isEditor()) base['X-PCP-User'] = getCurrentUser();
  return Object.assign(base, extra || {});
}

function aplicarEstadoServidor(dados){
  orders = limparParaArray(dados.orders);
  sections = limparParaArray(dados.sections);
  manualCPD = limparParaObjeto(dados.manualCPD);
  syncVersion = Number(dados.version || 0);
  ultimaAtualizacaoBanco = dados.updated_at || '';
  backendAtivo = true;
  setConnStatus('ok', 'Conectado');
  render();
}

async function tentarMigrarLocalStorageAntigo(){
  try{
    const raw = window.localStorage ? window.localStorage.getItem('pcp_mtr_topura_v2') : null;
    const jaMigrou = window.localStorage ? window.localStorage.getItem('pcp_sqlite_migrado_v1') : '1';
    if(!raw || jaMigrou) return;
    const antigo = JSON.parse(raw);
    const temDados = (Array.isArray(antigo.orders) && antigo.orders.length) || (Array.isArray(antigo.sections) && antigo.sections.length);
    if(!temDados) return;
    if(confirm('Encontrei dados antigos salvos neste navegador. Deseja importar para o banco central agora?')){
      await apiJSON('/api/import-json', 'POST', antigo);
      window.localStorage.setItem('pcp_sqlite_migrado_v1', '1');
      alert('Dados antigos importados para o banco central.');
    }
  }catch(e){
    console.warn('Migração local ignorada:', e);
  }
}

async function carregarServidor(forcarMensagem){
  if(carregandoBanco) return;
  carregandoBanco = true;
  try{
    if(forcarMensagem) setConnStatus('loading','Atualizando...');
    const resp = await fetch('/api/state?_=' + Date.now(), {cache:'no-store'});
    if(!resp.ok) throw new Error(await resp.text());
    const dados = await resp.json();
    aplicarEstadoServidor(dados);
    if((!dados.orders || dados.orders.length === 0) && (!dados.sections || dados.sections.length === 0)){
      await tentarMigrarLocalStorageAntigo();
    }
  }catch(e){
    console.error('Erro ao carregar banco:', e);
    backendAtivo = false;
    setConnStatus('erro','Servidor indisponível — alterações bloqueadas');
  }finally{
    carregandoBanco = false;
  }
}

async function verificarAtualizacoesServidor(){
  if(!backendAtivo || carregandoBanco) return;
  try{
    const resp = await fetch('/api/meta?_=' + Date.now(), {cache:'no-store'});
    if(!resp.ok) throw new Error(await resp.text());
    const meta = await resp.json();
    if(Number(meta.version || 0) !== Number(syncVersion || 0)) await carregarServidor(false);
  }catch(e){
    console.warn('Falha ao verificar atualização do banco:', e);
    backendAtivo = false;
    setConnStatus('erro','Conexão perdida — tentando reconectar');
  }
}

async function apiJSON(url, metodo, payload){
  try{
    const resp = await fetch(url, {
      method: metodo || 'POST',
      headers: authHeaders({'Content-Type':'application/json'}),
      body: payload === undefined ? undefined : JSON.stringify(payload),
      cache: 'no-store'
    });
    if(!resp.ok) throw new Error(await resp.text());
    const dados = await resp.json();
    aplicarEstadoServidor(dados);
    return dados;
  }catch(e){
    console.error('Erro ao salvar no banco:', e);
    setConnStatus('erro','Erro ao salvar — verifique o servidor');
    alert('Não consegui salvar no banco central. A tela será recarregada do servidor para evitar perda de dados.');
    await carregarServidor(true);
    throw e;
  }
}

function salvarLocal(){
  // Desativado de propósito: os dados agora ficam no SQLite central, não no navegador.
}
function carregarLocal(){
  // Desativado de propósito: carregar do navegador causava conflito entre computadores.
}

function initBackend(){
  setConnStatus('loading','Conectando...');
  carregarServidor(true);
  setInterval(verificarAtualizacoesServidor, 3000);
}

function exportarExcel(){
  window.location.href = '/api/export.xlsx';
}
async function gerarBackupAgora(){
  if(!exigirEdicao()) return;
  try{
    await apiJSON('/api/backup-now', 'POST', {});
    alert('Backup gerado na pasta backups do servidor.');
  }catch(e){
    alert('Não consegui gerar backup agora.');
  }
}

async function recarregarCpdsExcel(){
  if(!exigirEdicao()) return;
  if(!confirm('Recarregar a aba "Base CPDs" do arquivo dados_pcp.xlsx para a tela?')) return;
  try{
    setConnStatus('loading','Atualizando CPDs do Excel...');
    const resp = await fetch('/api/cpds/reload-excel', {method:'POST', headers: authHeaders(), cache:'no-store'});
    if(!resp.ok) throw new Error(await resp.text());
    const dados = await resp.json();
    aplicarEstadoServidor(dados);
    const qtd = dados.imported && dados.imported.cpds !== undefined ? dados.imported.cpds : 0;
    alert('Base de CPDs atualizada. CPDs lidos: ' + qtd);
  }catch(e){
    console.error('Erro ao atualizar CPDs:', e);
    alert('Não consegui recarregar a aba Base CPDs. Verifique se o arquivo dados_pcp.xlsx existe e não está corrompido.');
    await carregarServidor(true);
  }
}

async function importarExcel(input){
  if(!exigirEdicao()) { input.value=''; return; }
  const file = input.files && input.files[0];
  if(!file) return;
  if(!confirm('Importar este Excel para a base central? Pedidos com o mesmo Nº ou ID interno serão atualizados.')){
    input.value = '';
    return;
  }
  const form = new FormData();
  form.append('file', file);
  try{
    setConnStatus('loading','Importando Excel...');
    const resp = await fetch('/api/import.xlsx', {method:'POST', headers: authHeaders(), body:form});
    if(!resp.ok) throw new Error(await resp.text());
    const dados = await resp.json();
    aplicarEstadoServidor(dados);
    alert('Excel importado com sucesso.');
  }catch(e){
    console.error('Erro importando Excel:', e);
    alert('Não consegui importar o Excel. Verifique se ele está no modelo exportado pelo sistema.');
    await carregarServidor(true);
  }finally{
    input.value = '';
  }
}

function uid(){return Date.now().toString(36)+Math.random().toString(36).slice(2,6);}
function pad2(v){ return String(v).padStart(2,'0'); }
function todayStr(){const d=new Date();return d.getFullYear()+'-'+pad2(d.getMonth()+1)+'-'+pad2(d.getDate());}
function nowLocalStr(){
  const d = new Date();
  return d.getFullYear()+'-'+pad2(d.getMonth()+1)+'-'+pad2(d.getDate())+' '+pad2(d.getHours())+':'+pad2(d.getMinutes())+':'+pad2(d.getSeconds());
}
function parseDateInput(value){
  const text = String(value || '').trim();
  if(!text) return '';
  const iso = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if(iso) return iso[1]+'-'+iso[2]+'-'+iso[3];
  const normalized = text.replace(/[./]/g,'-');
  let m = normalized.match(/^(\d{1,2})-(\d{1,2})-(\d{2}|\d{4})$/);
  if(m){
    let d = Number(m[1]), mo = Number(m[2]), y = Number(m[3]);
    if(y < 100) y += 2000;
    const dt = new Date(y, mo-1, d);
    if(dt.getFullYear() === y && dt.getMonth() === mo-1 && dt.getDate() === d){
      return y+'-'+pad2(mo)+'-'+pad2(d);
    }
  }
  m = normalized.match(/^(\d{1,2})-(\d{1,2})$/);
  if(m){
    const y = new Date().getFullYear();
    const d = Number(m[1]), mo = Number(m[2]);
    const dt = new Date(y, mo-1, d);
    if(dt.getFullYear() === y && dt.getMonth() === mo-1 && dt.getDate() === d){
      return y+'-'+pad2(mo)+'-'+pad2(d);
    }
  }
  return '';
}
function proximaSextaFeira(){
  const d = new Date(); d.setHours(0,0,0,0);
  const dow = d.getDay(); // 0=dom ... 5=sex ... 6=sab
  const diff = (5 - dow + 7) % 7; // 0 se hoje já é sexta
  d.setDate(d.getDate()+diff);
  return d.getFullYear()+'-'+pad2(d.getMonth()+1)+'-'+pad2(d.getDate());
}
function sextaSemanasFrente(n){
  const d = new Date(proximaSextaFeira()+'T00:00:00');
  d.setDate(d.getDate() + (n*7));
  return d.getFullYear()+'-'+pad2(d.getMonth()+1)+'-'+pad2(d.getDate());
}
function fmtDate(s){
  if(!s) return '—';
  const iso = parseDateInput(s);
  if(!iso) return String(s);
  const [y,m,d] = iso.split('-');
  return d+'-'+m+'-'+y;
}
function fmtDateTime(s){
  if(!s) return '—';
  const text = String(s);
  const data = fmtDate(text.slice(0,10));
  const hora = text.length > 10 ? text.slice(11,16) : '';
  return hora ? data+' '+hora : data;
}
function fmtShortDate(s){
  if(!s) return '—';
  const iso = parseDateInput(s);
  if(!iso) return String(s);
  const [y,m,d] = iso.split('-');
  return d+'/'+m;
}
function sectionLabel(s){ return fmtShortDate((s && s.defaultDate) || (s && s.name) || ''); }
function diasEntre(a,b){ return Math.round((new Date(parseDateInput(b)+'T00:00:00') - new Date(parseDateInput(a)+'T00:00:00'))/86400000); }

document.getElementById('cur-date').textContent = new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'2-digit',year:'numeric'});

/* preencher selects estáticos */
(function initSelects(){
  const cli = document.getElementById('f-cliente');
  CLIENTES.forEach(c=>{ const o=document.createElement('option'); o.textContent=c; cli.appendChild(o); });
  const fs = document.getElementById('filter-setor');
  if(fs) SETORES.forEach(s=>{ const o=document.createElement('option'); o.value=s; o.textContent=s; fs.appendChild(o); });
})();

function refreshSecaoSelect(){
  const sel = document.getElementById('f-secao');
  sel.innerHTML='';

  // Ao abrir um novo pedido, usar a data/semana que está selecionada na tela.
  // Antes o formulário sempre caía na última data marcada como ativa, o que gerava pedidos na semana errada.
  let targetSectionId = '';
  if(sectionFilter && sectionFilter !== 'todas' && sections.some(s=>s.id===sectionFilter)){
    targetSectionId = sectionFilter;
  } else {
    const ativa = sections.find(s=>s.active);
    targetSectionId = ativa ? ativa.id : (sections[sections.length-1] && sections[sections.length-1].id) || '';
  }

  sections.forEach(s=>{
    const o=document.createElement('option');
    o.value=s.id;
    o.textContent=sectionLabel(s)+(s.active?' (ativa)':'');
    if(s.id === targetSectionId) o.selected=true;
    sel.appendChild(o);
  });
  onSecaoFormChange();
}

function onSecaoFormChange(){
  const sel = document.getElementById('f-secao');
  const sec = sections.find(s=>s.id===sel.value);
  if(sec && sec.defaultDate) document.getElementById('f-entrega').value = fmtDate(sec.defaultDate);
}

/* ===================== FORM ===================== */
function toggleForm(){
  if(!exigirEdicao()) return;
  const fb=document.getElementById('form-box');
  if(!fb.classList.contains('open') && sections.length===0){
    alert('Crie uma data antes de cadastrar o primeiro pedido.');
    novaSecao();
    if(sections.length===0) return; // criação cancelada
  }
  fb.classList.toggle('open');
  if(fb.classList.contains('open')){ refreshSecaoSelect(); setTimeout(()=>document.getElementById('f-cpd').focus(),60); }
}

function onSetorChange(){
  const v=document.getElementById('f-setor').value;
  document.getElementById('f-setor-outro-wrap').style.display = v==='Outro' ? 'block' : 'none';
}

function onCpdInput(){
  const code = document.getElementById('f-cpd').value.trim();
  const statusEl = document.getElementById('cpd-status');
  const descEl = document.getElementById('f-desc');
  if(!code){ statusEl.textContent=''; statusEl.className='cpd-status'; return; }
  const found = manualCPD[code] || CPD_MAP[code];
  if(found){
    descEl.value = found;
    statusEl.textContent = 'CPD encontrado na base.';
    statusEl.className = 'cpd-status found';
  } else {
    statusEl.innerHTML = 'CPD não encontrado na base. <button class="small" onclick="cadastrarNovoCpd()">Cadastrar este CPD</button>';
    statusEl.className = 'cpd-status notfound';
  }
}


async function cadastrarNovoCpd(){
  if(!exigirEdicao()) return;
  const code = document.getElementById('f-cpd').value.trim();
  const desc = document.getElementById('f-desc').value.trim();
  if(!code || !desc){ alert('Preencha o CPD e a descrição antes de cadastrar.'); return; }
  manualCPD[code] = desc;
  document.getElementById('cpd-status').textContent = 'CPD cadastrado com sucesso.';
  document.getElementById('cpd-status').className = 'cpd-status found';
  await apiJSON('/api/cpd/'+encodeURIComponent(code), 'PUT', {codigo:code, descricao:desc});
}


async function addOrder(){
  if(!exigirEdicao()) return;
  const cpd = document.getElementById('f-cpd').value.trim();
  const setor = document.getElementById('f-setor').value;
  const setorOutro = document.getElementById('f-setor-outro').value.trim();
  const entrega = parseDateInput(document.getElementById('f-entrega').value);
  const cliente = document.getElementById('f-cliente').value;
  const secaoId = document.getElementById('f-secao').value;

  if(!backendAtivo){ alert('O banco central não está conectado. Não vou salvar localmente para evitar perda de dados.'); return; }
  if(!cpd){ alert('Informe o CPD.'); document.getElementById('f-cpd').focus(); return; }
  if(setor==='Outro' && !setorOutro){ alert('Detalhe do setor é obrigatório quando "Outro" é selecionado.'); document.getElementById('f-setor-outro').focus(); return; }
  if(!entrega){ alert('Informe a data de entrega no formato DD-MM-AAAA.'); document.getElementById('f-entrega').focus(); return; }
  if(!secaoId){ alert('Crie ou selecione uma data antes de salvar.'); return; }

  const id = uid();
  const novoPedido = {
    id,
    cpd, descricao: document.getElementById('f-desc').value.trim(),
    setor, setorOutro,
    qtd: document.getElementById('f-qtd').value.trim(),
    dataEntregaOriginal: entrega,
    dataEntregaAtual: entrega,
    historico: [],
    previsao: parseDateInput(document.getElementById('f-previsao').value),
    obs: document.getElementById('f-obs').value.trim(),
    cliente,
    secaoId,
    dataConclusao: setor==='Concluído' ? todayStr() : null,
    criadoPor: getCurrentUser(),
    criadoEm: nowLocalStr(),
    alteradoPor: getCurrentUser(),
    alteradoEm: nowLocalStr(),
  };

  await apiJSON('/api/orders/'+encodeURIComponent(id), 'PUT', novoPedido);

  ['f-cpd','f-desc','f-setor-outro','f-qtd','f-entrega','f-previsao','f-obs'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('f-setor-outro-wrap').style.display='none';
  document.getElementById('cpd-status').textContent='';
  toggleForm();
}

/* ===================== DATAS ===================== */

async function novaSecao(){
  if(!exigirEdicao()) return;
  const sugestao = fmtDate(proximaSextaFeira());
  const dataDigitada = prompt('Data do novo grupo (DD-MM-AAAA):', sugestao);
  if(dataDigitada===null) return;
  const defaultDate = parseDateInput(dataDigitada);
  if(!defaultDate){ alert('Informe uma data válida no formato DD-MM-AAAA.'); return; }

  const id = 'sec'+uid();
  const novaSec = {id, name:fmtDate(defaultDate), defaultDate, active:true, criadoPor:getCurrentUser(), criadoEm:nowLocalStr(), alteradoPor:getCurrentUser(), alteradoEm:nowLocalStr()};
  sections.forEach(s=>s.active=false);
  sections.push(novaSec);
  render();
  await apiJSON('/api/sections/'+encodeURIComponent(id), 'PUT', novaSec);
}

function limparFiltros(){
  const cpd = document.getElementById('filter-cpd');
  const grupo = document.getElementById('filter-grupo');
  const setor = document.getElementById('filter-setor');
  const previsao = document.getElementById('filter-previsao');
  if(cpd) cpd.value='';
  if(grupo) grupo.value='todos';
  if(setor) setor.value='todos';
  if(previsao) previsao.value='todos';
  render();
}

function setSectionFilter(id){ sectionFilter = id; render(); }

async function apagarSecao(sectionId){
  if(!exigirEdicao()) return;
  const sec = sections.find(s=>s.id===sectionId);
  if(!sec){ alert('Data não encontrada. Clique em Atualizar e tente novamente.'); return; }
  const label = sectionLabel(sec) || 'esta data';
  const vinculados = orders.filter(o=>o.secaoId===sectionId);
  let payload = {mode:'empty'};

  if(vinculados.length > 0){
    const aviso = 'A data ' + label + ' possui ' + vinculados.length + ' pedido(s).\n\n' +
      'Para apagar a data, o sistema também vai apagar TODOS os pedidos dessa data.\n' +
      'Essa ação fica registrada na aba Auditoria do Excel.\n\n' +
      'Para confirmar, digite APAGAR:';
    const digitado = prompt(aviso, '');
    if(digitado === null) return;
    if(String(digitado).trim().toUpperCase() !== 'APAGAR'){
      alert('Exclusão cancelada. Nada foi apagado.');
      return;
    }
    payload = {mode:'delete_orders'};
  } else {
    if(!confirm('Apagar a data ' + label + '?')) return;
  }

  if(sectionFilter === sectionId) sectionFilter = 'todas';
  await apiJSON('/api/sections/'+encodeURIComponent(sectionId), 'DELETE', payload);
}

/* Toda mudança de data de entrega (edição direta ou troca de data) passa por aqui.
   Se a data muda de fato, exige um motivo — sem motivo, a mudança inteira é cancelada. */
/* Retorna: null (nada muda), false (motivo recusado -> aborta) ou {dataEntregaAtual, historico} pra mesclar */
function aplicarMudancaData(o, novaData){
  if(!novaData || novaData===o.dataEntregaAtual) return null;
  let motivo = '';
  while(true){
    motivo = prompt('Motivo da alteração da data de entrega (obrigatório):', motivo);
    if(motivo===null) return false;
    motivo = motivo.trim();
    if(motivo) break;
    alert('O motivo é obrigatório quando a data de entrega muda.');
  }
  const novoHistorico = [...(o.historico||[]), {de:o.dataEntregaAtual, para:novaData, quando:todayStr(), usuario:getCurrentUser(), motivo}];
  return {dataEntregaAtual: novaData, historico: novoHistorico};
}


async function moveOrder(id, newSecId){
  if(!exigirEdicao()) { render(); return; }
  const o = orders.find(x=>x.id===id);
  if(!o) return;
  const novaSec = sections.find(s=>s.id===newSecId);
  const novaData = novaSec ? novaSec.defaultDate : null;
  const mudanca = aplicarMudancaData(o, novaData);
  if(mudanca===false){ render(); return; }
  const updates = {secaoId:newSecId};
  if(mudanca) Object.assign(updates, mudanca);
  Object.assign(o, updates);
  render();
  await apiJSON('/api/orders/'+encodeURIComponent(id), 'PATCH', updates);
}

/* ===================== SETOR ===================== */

async function onSetorEditChange(id, newSetor){
  if(!exigirEdicao()) { render(); return; }
  const o = orders.find(x=>x.id===id);
  if(!o) return;
  let setorOutro = o.setorOutro || '';
  if(newSetor==='Outro'){
    const detalhe = prompt('Detalhe do setor (obrigatório):', o.setorOutro||'');
    if(!detalhe){ render(); return; }
    setorOutro = detalhe;
  }

  const oldSetor = o.setor || '—';
  let motivoSetor = 'Alteração de setor/situação';
  if(newSetor === 'Cancelado' && oldSetor !== 'Cancelado'){
    motivoSetor = '';
    while(!motivoSetor){
      const digitado = prompt('Motivo do cancelamento (obrigatório):', '');
      if(digitado === null){ render(); return; }
      motivoSetor = String(digitado || '').trim();
      if(!motivoSetor) alert('Informe o motivo do cancelamento.');
    }
  }
  const updates = {
    setor:newSetor,
    setorOutro,
    historico: [...(o.historico || []), {
      tipo: newSetor === 'Cancelado' ? 'cancelamento' : 'setor',
      de: oldSetor,
      para: newSetor,
      quando: todayStr(),
      usuario: getCurrentUser(),
      motivo: motivoSetor
    }]
  };
  if(newSetor === 'Concluído' && oldSetor !== 'Concluído') updates.dataConclusao = todayStr();
  if(newSetor !== 'Concluído' && oldSetor === 'Concluído') updates.dataConclusao = null;
  Object.assign(o, updates);
  render();
  await apiJSON('/api/orders/'+encodeURIComponent(id), 'PATCH', updates);
}


async function editEntrega(id){
  if(!exigirEdicao()) return;
  const o = orders.find(x=>x.id===id);
  if(!o) return;
  const digitado = prompt('Nova data de entrega (DD-MM-AAAA):', fmtDate(o.dataEntregaAtual));
  if(!digitado) return;
  const novo = parseDateInput(digitado);
  if(!novo){ alert('Informe uma data válida no formato DD-MM-AAAA.'); return; }
  const mudanca = aplicarMudancaData(o, novo);
  if(mudanca===false){ render(); return; }
  if(mudanca===null) return;
  Object.assign(o, mudanca);
  render();
  await apiJSON('/api/orders/'+encodeURIComponent(id), 'PATCH', mudanca);
}

async function editPrevisao(id){
  if(!exigirEdicao()) return;
  const o = orders.find(x=>x.id===id);
  if(!o) return;
  const atual = o.previsao ? fmtDate(o.previsao) : '';
  const digitado = prompt('Nova previsão de retorno (DD-MM-AAAA). Deixe em branco para limpar:', atual);
  if(digitado === null) return;
  const texto = String(digitado || '').trim();
  const novaPrevisao = texto ? parseDateInput(texto) : '';
  if(texto && !novaPrevisao){ alert('Informe uma data válida no formato DD-MM-AAAA.'); return; }
  if((o.previsao || '') === novaPrevisao) return;
  const updates = {
    previsao: novaPrevisao,
    historico: [...(o.historico || []), {
      tipo: 'previsao',
      de: o.previsao || '',
      para: novaPrevisao || '',
      quando: todayStr(),
      usuario: getCurrentUser(),
      motivo: 'Alteração de previsão de retorno'
    }]
  };
  Object.assign(o, updates);
  render();
  await apiJSON('/api/orders/'+encodeURIComponent(id), 'PATCH', updates);
}


async function editObservacao(id){
  if(!exigirEdicao()) return;
  const o = orders.find(x=>x.id===id);
  if(!o) return;
  const digitado = prompt('Alterar observação:', o.obs || '');
  if(digitado === null) return;
  const novaObs = String(digitado || '').trim();
  if((o.obs || '') === novaObs) return;
  const updates = {
    obs: novaObs,
    historico: [...(o.historico || []), {
      tipo: 'observacao',
      de: o.obs || '',
      para: novaObs,
      quando: todayStr(),
      usuario: getCurrentUser(),
      motivo: 'Alteração de observação'
    }]
  };
  Object.assign(o, updates);
  render();
  await apiJSON('/api/orders/'+encodeURIComponent(id), 'PATCH', updates);
}

function toggleHist(id){
  if(expandedHist.has(id)) expandedHist.delete(id); else expandedHist.add(id);
  render();
}


async function removeOrder(id){
  if(!exigirEdicao()) return;
  const motivo = prompt('Motivo para enviar este pedido para a lixeira:', 'Removido pela tela');
  if(motivo === null) return;
  orders = orders.filter(x=>x.id!==id);
  render();
  await apiJSON('/api/orders/'+encodeURIComponent(id), 'DELETE', {motivo: motivo || 'Removido pela tela'});
}

let trashCache = {orders:[], sections:[]};
async function carregarLixeira(){
  const painel = document.getElementById('trash-panel');
  if(!painel) return;
  painel.innerHTML = '<div class="empty">Carregando lixeira...</div>';
  try{
    const resp = await fetch('/api/trash?_=' + Date.now(), {cache:'no-store', headers: authHeaders()});
    if(!resp.ok) throw new Error(await resp.text());
    trashCache = await resp.json();
    renderLixeira();
  }catch(e){
    console.error(e);
    painel.innerHTML = '<div class="empty">Não consegui carregar a lixeira.</div>';
  }
}

async function restaurarItem(tipo, id, includeOrders){
  if(!exigirEdicao()) return;
  const payload = tipo === 'section' ? {include_orders: !!includeOrders} : {};
  await apiJSON('/api/trash/restore/'+encodeURIComponent(tipo)+'/'+encodeURIComponent(id), 'POST', payload);
  await carregarLixeira();
}

function renderLixeira(){
  const painel = document.getElementById('trash-panel');
  const pedidos = trashCache.orders || [];
  const datas = trashCache.sections || [];
  if(!pedidos.length && !datas.length){
    painel.innerHTML = '<div class="empty">Lixeira vazia.</div>';
    return;
  }
  const datasHtml = datas.map(s=>`<div class="order"><div class="order-row"><b>Data ${fmtDate(s.defaultDate)}</b><span class="badge">Apagada por ${s.deletedBy||'—'}</span><span class="badge">${s.deletedAt||''}</span>${isEditor()?`<button class="small" onclick="restaurarItem('section','${s.id}',true)">Restaurar data e pedidos</button><button class="small" onclick="restaurarItem('section','${s.id}',false)">Restaurar só data</button>`:''}</div><div class="order-meta"><span>Motivo: ${s.deleteReason||'—'}</span></div></div>`).join('');
  const pedidosHtml = pedidos.map(o=>`<div class="order"><div class="order-row"><span class="order-cpd">${o.cpd||'—'}</span><span class="order-desc">${o.descricao||''}</span><span class="badge">${o.setor||'—'}</span><span class="badge">Apagado por ${o.deletedBy||'—'}</span>${isEditor()?`<button class="small" onclick="restaurarItem('order','${o.id}',false)">Restaurar pedido</button>`:''}</div><div class="order-meta"><span>Motivo: ${o.deleteReason||'—'}</span><span>Apagado em: ${o.deletedAt||'—'}</span></div></div>`).join('');
  painel.innerHTML = `<div class="orders-section-group"><div class="group-divider"><span class="label">Datas apagadas <span class="count">(${datas.length})</span></span><span class="line"></span></div>${datasHtml||'<div class="empty">Nenhuma data na lixeira.</div>'}</div><div class="orders-section-group"><div class="group-divider"><span class="label">Pedidos apagados <span class="count">(${pedidos.length})</span></span><span class="line"></span></div>${pedidosHtml||'<div class="empty">Nenhum pedido na lixeira.</div>'}</div>`;
}

/* ===================== CÁLCULOS DE BADGE ===================== */
function prazoBadge(dataEntregaAtual){
  const today = new Date(); today.setHours(0,0,0,0);
  const d = new Date(dataEntregaAtual+'T00:00:00');
  const diff = Math.round((d-today)/86400000);
  if(diff<0) return {label:'Vencido', cls:'b-vencido'};
  if(diff<=7) return {label:'Esta semana', cls:'b-atrasado'};
  if(diff<=14) return {label:'Atenção', cls:'b-atencao'};
  return {label:'No prazo', cls:'b-noprazo'};
}
function driftBadge(o){
  if(o.dataEntregaAtual===o.dataEntregaOriginal) return null;
  if(o.dataEntregaAtual < o.dataEntregaOriginal) return {label:'Adiantado', cls:'b-adiantado'};
  return {label:'Postergado', cls:'b-postergado'};
}
function clienteGrupo(cliente){ return HONDA_GROUP.includes(cliente) ? 'HONDA' : 'DIVERSOS'; }
function entregaAtrasoLabel(o){
  if(!o.dataConclusao) return null;
  return o.dataConclusao > o.dataEntregaAtual ? {label:'Atraso',cls:'b-vencido'} : {label:'No prazo',cls:'b-noprazo'};
}

/* ===================== TABS ===================== */
function setTab(t){
  if(!isEditor() && (t==='kpi' || t==='anotacoes' || t==='lixeira')) t='ativa';
  currentTab=t;
  document.getElementById('tab-ativa').classList.toggle('on', t==='ativa');
  document.getElementById('tab-entregues').classList.toggle('on', t==='entregues');
  document.getElementById('tab-kpi').classList.toggle('on', t==='kpi');
  const tabAnotacoes = document.getElementById('tab-anotacoes'); if(tabAnotacoes) tabAnotacoes.classList.toggle('on', t==='anotacoes');
  const tabLixeira = document.getElementById('tab-lixeira'); if(tabLixeira) tabLixeira.classList.toggle('on', t==='lixeira');
  const isSpecial = t==='kpi' || t==='lixeira' || t==='anotacoes';
  document.getElementById('sections-bar').style.display = isSpecial ? 'none' : 'flex';
  const sortBar = document.getElementById('sort-bar'); if(sortBar) sortBar.style.display = isSpecial ? 'none' : 'flex';
  const filtersBar = document.getElementById('filters-bar'); if(filtersBar) filtersBar.style.display = isSpecial ? 'none' : 'flex';
  document.getElementById('orders-list').style.display = isSpecial ? 'none' : 'block';
  document.getElementById('kpi-panel').style.display = t==='kpi' ? 'block' : 'none';
  const notesPanel = document.getElementById('notes-panel'); if(notesPanel) notesPanel.style.display = t==='anotacoes' ? 'block' : 'none';
  const trashPanel = document.getElementById('trash-panel'); if(trashPanel) trashPanel.style.display = t==='lixeira' ? 'block' : 'none';
  if(t==='lixeira') carregarLixeira();
  if(t==='anotacoes') renderNotas();
  render();
}

/* ===================== RENDER ===================== */
function render(){
  // resumo
  const ativos = orders.filter(o=>!isFinalizado(o));
  const concluidos = orders.filter(o=>computeStatus(o)==='concluido');
  document.getElementById('c-total').textContent = ativos.length;
  document.getElementById('c-pend').textContent = ativos.length;
  document.getElementById('c-atrasado').textContent = ativos.filter(o=>{const b=prazoBadge(o.dataEntregaAtual);return b.cls==='b-atrasado'||b.cls==='b-vencido';}).length;
  document.getElementById('c-done').textContent = concluidos.length;

  renderAttentionPanel();
  if(currentTab==='kpi'){ renderKPI(); return; }
  if(currentTab==='anotacoes'){ renderNotas(); return; }
  if(currentTab==='lixeira'){ return; }

  // barra de datas
  const bar = document.getElementById('sections-bar');
  bar.innerHTML = sections.map(s=>{
    const activeCount = orders.filter(o=>o.secaoId===s.id && !isFinalizado(o)).length;
    const doneCount = orders.filter(o=>o.secaoId===s.id && isFinalizado(o)).length;
    const visibleCount = currentTab === 'ativa' ? activeCount : doneCount;
    if(visibleCount === 0) return '';
    const label = sectionLabel(s) + ' (' + visibleCount + ')';
    return `<span class="sec-pill-wrap"><button class="sec-pill ${sectionFilter===s.id?'on':''}" onclick="setSectionFilter('${s.id}')">${s.active && currentTab==='ativa'?'<span class="dot"></span>':''}${label}</button></span>`;
  }).join('') + `<button class="sec-pill ${sectionFilter==='todas'?'on':''}" onclick="setSectionFilter('todas')">Todas</button>` + `${isEditor()?`<button class="small" onclick="novaSecao()">+ Nova data</button>`:''}`;

  const list = document.getElementById('orders-list');

  let pool = currentTab==='ativa' ? orders.filter(o=>!isFinalizado(o)) : orders.filter(o=>isFinalizado(o));
  if(sectionFilter!=='todas') pool = pool.filter(o=>o.secaoId===sectionFilter);
  const cpdBusca = String((document.getElementById('filter-cpd') || {}).value || '').trim().toLowerCase();
  const grupoFiltro = String((document.getElementById('filter-grupo') || {}).value || 'todos');
  const setorFiltro = String((document.getElementById('filter-setor') || {}).value || 'todos');
  const previsaoFiltro = String((document.getElementById('filter-previsao') || {}).value || 'todos');
  if(cpdBusca) pool = pool.filter(o=>String(o.cpd||'').toLowerCase().includes(cpdBusca));
  if(grupoFiltro !== 'todos') pool = pool.filter(o=>clienteGrupo(o.cliente) === grupoFiltro);
  if(setorFiltro !== 'todos') pool = pool.filter(o=>String(o.setor||'') === setorFiltro);
  if(previsaoFiltro === 'sem') pool = pool.filter(o=>!o.previsao);
  if(previsaoFiltro === 'com') pool = pool.filter(o=>!!o.previsao);
  const sortMode = (document.getElementById('sort-mode') || {}).value || 'grupo';
  if(sortMode==='atraso') pool.sort(compareAtrasoProcesso);
  else if(sortMode==='entrega') pool.sort((a,b)=>String(a.dataEntregaAtual||'').localeCompare(String(b.dataEntregaAtual||'')));
  else if(sortMode==='cpd') pool.sort((a,b)=>String(a.cpd||'').localeCompare(String(b.cpd||'')));

  if(!pool.length){
    list.innerHTML = `<div class="empty">${currentTab==='ativa' ? 'Nenhum pedido pendente nesta visão/filtro.' : 'Nenhum pedido finalizado nesta visão/filtro.'}</div>`;
    return;
  }

  // agrupar por data/semana sempre, inclusive na visão Todas.
  const bySec = {};
  pool.forEach(o=>{ (bySec[o.secaoId] = bySec[o.secaoId]||[]).push(o); });

  list.innerHTML = Object.keys(bySec).sort((a,b)=>{
    const sa=sections.find(s=>s.id===a)||{}; const sb=sections.find(s=>s.id===b)||{};
    return String(sa.defaultDate||'').localeCompare(String(sb.defaultDate||''));
  }).map(secId=>{
    const sec = (sections.find(s=>s.id===secId) || {name:'', defaultDate:''});
    const items = bySec[secId];
    if(sortMode==='atraso') items.sort(compareAtrasoProcesso);
    else if(sortMode==='entrega') items.sort((a,b)=>String(a.dataEntregaAtual||'').localeCompare(String(b.dataEntregaAtual||'')));
    else if(sortMode==='cpd') items.sort((a,b)=>String(a.cpd||'').localeCompare(String(b.cpd||'')));
    const cardsHtml = items.map(o=>renderCard(o, sec)).join('');
    return `<div class="orders-section-group">
      <div class="group-divider">
        <span class="label">${sectionLabel(sec)} ${sec.active?'<span class="active-tag">ativa</span>':''} <span class="count">(${items.length})</span></span>
        <span class="line"></span>
        ${sec && sec.id && isEditor() ? `<button class="small danger" onclick="apagarSecao('${secId}')">apagar data</button>` : ''}
      </div>
      ${cardsHtml}
    </div>`;
  }).join('');
}

function renderKPI(){
  const panel = document.getElementById('kpi-panel');
  const total = orders.length;
  if(!total){
    panel.innerHTML = '<div class="kpi-card full"><p class="kpi-empty">Sem pedidos cadastrados ainda — os indicadores aparecem aqui depois do primeiro pedido.</p></div>';
    return;
  }

  // 1. % entregue no prazo vs com atraso (só pedidos concluídos)
  const concluidos = orders.filter(o=>computeStatus(o)==='concluido');
  const noPrazo = concluidos.filter(o=>{const e=entregaAtrasoLabel(o); return e && e.label==='No prazo';}).length;
  const comAtraso = concluidos.filter(o=>{const e=entregaAtrasoLabel(o); return e && e.label==='Atraso';}).length;
  const pctPrazo = concluidos.length ? Math.round(noPrazo/concluidos.length*100) : 0;

  // 2. Pedidos ativos por setor (onde estão parados)
  const ativos = orders.filter(o=>!isFinalizado(o));
  const porSetor = {};
  ativos.forEach(o=>{ porSetor[o.setor]=(porSetor[o.setor]||0)+1; });
  const setorEntries = Object.entries(porSetor).sort((a,b)=>b[1]-a[1]);
  const maxSetor = setorEntries.length ? setorEntries[0][1] : 1;

  // 3. Adiantado vs Postergado (estado atual, todos os pedidos)
  let nAdiantado=0, nPostergado=0, nSemAlt=0, somaAdiant=0, somaPosterg=0;
  orders.forEach(o=>{
    const db = driftBadge(o);
    if(!db){ nSemAlt++; return; }
    if(db.label==='Adiantado'){ nAdiantado++; somaAdiant += diasEntre(o.dataEntregaAtual, o.dataEntregaOriginal); }
    else { nPostergado++; somaPosterg += diasEntre(o.dataEntregaOriginal, o.dataEntregaAtual); }
  });
  const mediaAdiant = nAdiantado ? (somaAdiant/nAdiantado).toFixed(1) : '—';
  const mediaPosterg = nPostergado ? (somaPosterg/nPostergado).toFixed(1) : '—';

  // 4. Volume HONDA vs DIVERSOS
  const nHonda = orders.filter(o=>clienteGrupo(o.cliente)==='HONDA').length;
  const nDiversos = total - nHonda;
  const pctHonda = Math.round(nHonda/total*100);


  const semPrevisao = ativos.filter(o=>!o.previsao).length;
  const vencidos = ativos.filter(o=>prazoBadge(o.dataEntregaAtual).cls==='b-vencido').length;
  const setorCountsGeral = {};
  orders.forEach(o=>{ const lbl=o.setor || '(vazio)'; setorCountsGeral[lbl]=(setorCountsGeral[lbl]||0)+1; });
  const statusEntries = Object.entries(setorCountsGeral).sort((a,b)=>b[1]-a[1]);
  const topCpdsMap = {};
  orders.forEach(o=>{ if(o.cpd) topCpdsMap[o.cpd]=(topCpdsMap[o.cpd]||0)+1; });
  const topCpds = Object.entries(topCpdsMap).sort((a,b)=>b[1]-a[1]).slice(0,5);

  // 5. Médias por semana e por mês — volume, % no prazo, desvio de data
  function statsDoGrupo(items){
    const conc = items.filter(o=>computeStatus(o)==='concluido');
    const np = conc.filter(o=>{const e=entregaAtrasoLabel(o); return e&&e.label==='No prazo';}).length;
    const pct = conc.length ? (np/conc.length*100) : null;
    const drifts = items.map(o=>{
      const db = driftBadge(o);
      if(!db) return null;
      return db.label==='Adiantado' ? -diasEntre(o.dataEntregaAtual,o.dataEntregaOriginal) : diasEntre(o.dataEntregaOriginal,o.dataEntregaAtual);
    }).filter(v=>v!==null);
    const avgDrift = drifts.length ? drifts.reduce((a,b)=>a+b,0)/drifts.length : null;
    return {volume: items.length, pct, avgDrift};
  }
  function media(vals){ const v=vals.filter(x=>x!==null && x!==undefined); return v.length ? v.reduce((a,b)=>a+b,0)/v.length : null; }
  function fmtPct(v){ return v===null ? '—' : v.toFixed(0)+'%'; }
  function fmtDias(v){ return v===null ? '—' : (v>0?'+':'')+v.toFixed(1)+'d'; }

  const bySemana = {};
  orders.forEach(o=>{ (bySemana[o.secaoId]=bySemana[o.secaoId]||[]).push(o); });
  const statsPorSemana = Object.keys(bySemana).map(secId=>statsDoGrupo(bySemana[secId]));

  const porMes = {};
  orders.forEach(o=>{
    const sec = sections.find(s=>s.id===o.secaoId);
    const mes = sec ? sec.defaultDate.slice(0,7) : 'sem-secao';
    (porMes[mes]=porMes[mes]||[]).push(o);
  });
  const statsPorMes = Object.keys(porMes).map(mes=>statsDoGrupo(porMes[mes]));

  const volMedioSemana = media(statsPorSemana.map(s=>s.volume));
  const pctMedioSemana = media(statsPorSemana.map(s=>s.pct));
  const driftMedioSemana = media(statsPorSemana.map(s=>s.avgDrift));

  const volMedioMes = media(statsPorMes.map(s=>s.volume));
  const pctMedioMes = media(statsPorMes.map(s=>s.pct));
  const driftMedioMes = media(statsPorMes.map(s=>s.avgDrift));

  panel.innerHTML = `
    <div class="kpi-grid">

      <div class="kpi-card">
        <h3>Entregas no prazo</h3>
        ${concluidos.length ? `
          <div class="kpi-big"><span class="num">${pctPrazo}%</span><span class="sub">no prazo de ${concluidos.length} concluídos</span></div>
          <div class="kpi-stackbar"><div class="seg-prazo" style="width:${pctPrazo}%"></div><div class="seg-atraso" style="width:${100-pctPrazo}%"></div></div>
          <div class="kpi-legend"><span><span class="dot" style="background:var(--green)"></span>No prazo: ${noPrazo}</span><span><span class="dot" style="background:var(--red)"></span>Atraso: ${comAtraso}</span></div>
        ` : `<p class="kpi-empty">Nenhum pedido concluído ainda.</p>`}
      </div>

      <div class="kpi-card">
        <h3>HONDA vs DIVERSOS</h3>
        <div class="kpi-big"><span class="num">${pctHonda}%</span><span class="sub">HONDA de ${total} pedidos no total</span></div>
        <div class="kpi-stackbar"><div class="seg-honda" style="width:${pctHonda}%"></div><div class="seg-diversos" style="width:${100-pctHonda}%"></div></div>
        <div class="kpi-legend"><span><span class="dot" style="background:#ef4444"></span>HONDA: ${nHonda}</span><span><span class="dot" style="background:var(--text3)"></span>DIVERSOS: ${nDiversos}</span></div>
      </div>

      <div class="kpi-card full">
        <h3>Pedidos ativos por setor (onde estão parados)</h3>
        ${setorEntries.length ? setorEntries.map(([setor,count])=>`
          <div class="kpi-bar-row">
            <span class="lbl">${setor}</span>
            <span class="track"><span class="fill" style="width:${Math.round(count/maxSetor*100)}%"></span></span>
            <span class="val">${count}</span>
          </div>`).join('') : '<p class="kpi-empty">Nenhum pedido ativo.</p>'}
      </div>



      <div class="kpi-card full">
        <h3>Indicadores de controle</h3>
        <div class="kpi-legend">
          <span><span class="dot" style="background:var(--red)"></span>Vencidos ativos: ${vencidos}</span>
          <span><span class="dot" style="background:var(--amber)"></span>Sem previsão de retorno: ${semPrevisao}</span>
          <span><span class="dot" style="background:var(--blue)"></span>Setores/situações principais: ${statusEntries.slice(0,4).map(([s,c])=>s+': '+c).join(' | ') || '—'}</span>
          <span><span class="dot" style="background:var(--teal)"></span>Top CPDs: ${topCpds.map(([c,n])=>c+' ('+n+')').join(', ') || '—'}</span>
        </div>
      </div>

      <div class="kpi-card full">
        <h3>Adiantado vs Postergado</h3>
        <div class="kpi-legend">
          <span><span class="dot" style="background:var(--teal)"></span>Adiantados: ${nAdiantado} (média ${mediaAdiant} dias)</span>
          <span><span class="dot" style="background:var(--purple)"></span>Postergados: ${nPostergado} (média ${mediaPosterg} dias)</span>
          <span><span class="dot" style="background:var(--text3)"></span>Sem alteração de data: ${nSemAlt}</span>
        </div>
      </div>

      <div class="kpi-card full">
        <h3>Médias por período (${statsPorSemana.length} semana(s) / ${statsPorMes.length} mês(es) com pedidos)</h3>
        <div class="kpi-grid">
          <div>
            <p style="font-size:11.5px;color:var(--text2);font-weight:700;margin-bottom:6px">Por semana</p>
            <div class="kpi-bar-row"><span class="lbl">Volume</span><span class="val" style="width:auto">${volMedioSemana===null?'—':volMedioSemana.toFixed(1)}</span></div>
            <div class="kpi-bar-row"><span class="lbl">% no prazo</span><span class="val" style="width:auto">${fmtPct(pctMedioSemana)}</span></div>
            <div class="kpi-bar-row"><span class="lbl">Desvio</span><span class="val" style="width:auto">${fmtDias(driftMedioSemana)}</span></div>
          </div>
          <div>
            <p style="font-size:11.5px;color:var(--text2);font-weight:700;margin-bottom:6px">Por mês</p>
            <div class="kpi-bar-row"><span class="lbl">Volume</span><span class="val" style="width:auto">${volMedioMes===null?'—':volMedioMes.toFixed(1)}</span></div>
            <div class="kpi-bar-row"><span class="lbl">% no prazo</span><span class="val" style="width:auto">${fmtPct(pctMedioMes)}</span></div>
            <div class="kpi-bar-row"><span class="lbl">Desvio</span><span class="val" style="width:auto">${fmtDias(driftMedioMes)}</span></div>
          </div>
        </div>
        <p class="kpi-empty" style="margin-top:8px">Desvio negativo = em média adiantando; positivo = em média postergando. "% no prazo" considera só pedidos já concluídos dentro do período.</p>
      </div>

    </div>
  `;
}

function renderCard(o, sec){
  const status = computeStatus(o);
  const cfg = STATUS_CFG[status];
  const grupo = clienteGrupo(o.cliente);
  const secOpts = sections.map(s=>`<option value="${s.id}"${s.id===o.secaoId?' selected':''}>${sectionLabel(s)}</option>`).join('');
  const setorOpts = SETORES.map(s=>`<option value="${s}"${o.setor===s?' selected':''}>${s}</option>`).join('');
  const editDisabled = isEditor() ? '' : ' disabled';
  const criadoPor = o.criadoPor || o.createdBy || '';
  const criadoEm = o.criadoEm || o.createdAt || '';
  const alteradoPor = o.alteradoPor || o.updatedBy || '';
  const alteradoEm = o.alteradoEm || o.updatedAt || '';

  let badgesHtml = '';
  if(currentTab==='ativa'){
    const pb = prazoBadge(o.dataEntregaAtual);
    badgesHtml += `<span class="badge ${pb.cls}">${pb.label}</span>`;
    const db = driftBadge(o);
    if(db) badgesHtml += `<span class="badge ${db.cls}">${db.label}</span>`;
  } else {
    const eb = entregaAtrasoLabel(o);
    if(eb) badgesHtml += `<span class="badge ${eb.cls}">${eb.label}</span>`;
  }
  badgesHtml += `<span class="badge ${grupo==='HONDA'?'b-honda':'b-diversos'}">${grupo}</span>`;
  badgesHtml += `<span class="badge" style="background:${cfg.bg};color:${cfg.col};border-color:${cfg.border}">${cfg.label}</span>`;

  const historicoEventos = [];
  if(criadoPor) historicoEventos.push(`<div>${criadoEm ? fmtDateTime(criadoEm) : '—'} — criado por ${criadoPor}</div>`);
  if(alteradoPor) historicoEventos.push(`<div>${alteradoEm ? fmtDateTime(alteradoEm) : '—'} — última alteração por ${alteradoPor}</div>`);
  (o.historico || []).forEach(h=>{
    const usuario = h.usuario ? ('por ' + h.usuario + ' — ') : '';
    if(h.tipo === 'previsao'){
      historicoEventos.push(`<div>${fmtDate(h.quando)} — ${usuario}previsão de retorno mudou de ${fmtDate(h.de)} para ${fmtDate(h.para)}</div>`);
    } else if(h.tipo === 'setor' || h.tipo === 'status'){
      historicoEventos.push(`<div>${fmtDate(h.quando)} — ${usuario}setor mudou de ${h.de||'—'} para ${h.para||'—'}</div>`);
    } else if(h.tipo === 'observacao'){
      historicoEventos.push(`<div>${fmtDate(h.quando)} — ${usuario}observação alterada de "${h.de||'—'}" para "${h.para||'—'}"</div>`);
    } else {
      historicoEventos.push(`<div>${fmtDate(h.quando)} — ${usuario}entrega mudou de ${fmtDate(h.de)} para ${fmtDate(h.para)} — motivo: ${h.motivo||'—'}</div>`);
    }
  });
  const histHtml = expandedHist.has(o.id) ? `<div class="hist-box">${
    historicoEventos.length ? historicoEventos.join('') : '<div>Sem histórico registrado.</div>'
  }</div>` : '';
  const urg = urgencyInfo(o);
  const urgBadge = urg.label ? `<span class="urgency-chip ${urg.cls==='risk-high'?'urgency-high':(urg.cls==='risk-mid'?'urgency-mid':(urg.cls==='risk-nylok'?'urgency-nylok':'urgency-low'))}">${urg.label}</span>` : '';

  return `<div class="order ${urg.cls}" style="border-left-color:${cfg.border}">
    <div class="order-row">
      <span class="order-cpd">${o.cpd}</span>
      <span class="order-desc" title="${o.descricao}">${o.descricao||'(sem descrição)'}</span>
      <select style="width:auto;padding:3px 6px;font-size:11px" onchange="onSetorEditChange('${o.id}',this.value)" title="${o.setor==='Outro'?('Outro: '+o.setorOutro):''}"${editDisabled}>${setorOpts}</select>
      <span class="badge">${o.cliente}</span>
      ${o.setor==='Outro' && o.setorOutro ? `<span class="badge">Outro: ${o.setorOutro}</span>` : ''}
      ${badgesHtml}
      ${urgBadge}
      <div class="order-actions">
        ${isEditor()?`<button class="ghost" onclick="removeOrder('${o.id}')" title="Remover">✕</button>`:''}
      </div>
    </div>
    <div class="order-meta">
      <span>Qtd faltante: <b>${o.qtd||'—'}</b></span>
      <span>Entrega: <b>${fmtDate(o.dataEntregaAtual)}</b> ${isEditor()?`<button class="small" onclick="editEntrega('${o.id}')">editar</button>`:''}</span>
      <span>Previsão retorno: <b>${fmtDate(o.previsao)}</b> ${isEditor()?`<button class="small" onclick="editPrevisao('${o.id}')">editar</button>`:''}</span>
      ${currentTab==='entregues' ? `<span>Concluído em: <b>${fmtDate(o.dataConclusao)}</b></span>` : ''}
      ${o.obs ? `<span>Obs: ${o.obs} ${isEditor()?`<button class="small" onclick="editObservacao('${o.id}')">editar</button>`:''}</span>` : (isEditor()?`<span>Obs: — <button class="small" onclick="editObservacao('${o.id}')">editar</button></span>`:'')}
      <button class="small" onclick="toggleHist('${o.id}')">${expandedHist.has(o.id)?'ocultar':'histórico'}</button>
      ${currentTab==='ativa' && isEditor() ? `<select style="width:auto;padding:3px 6px;font-size:11px" onchange="moveOrder('${o.id}',this.value)">${secOpts}</select>` : ''}
    </div>
    ${histHtml}
  </div>`;
}

render();
if(carregarAuthSalvo()) initBackend();
