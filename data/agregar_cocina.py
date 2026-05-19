import json

tipo_cocina = {
  1001:"mexicana", 1002:"mexicana", 1003:"internacional", 1004:"mexicana",
  1005:"mexicana", 1006:"mexicana", 1007:"mexicana", 1008:"mexicana",
  1009:"mexicana", 1010:"mexicana", 1011:"mexicana", 1012:"mexicana",
  1013:"mexicana", 1014:"internacional", 1015:"mexicana", 1016:"italiana",
  1017:"italiana", 1018:"italiana", 1019:"mexicana", 1020:"mexicana",
  1021:"mexicana", 1022:"internacional", 1023:"mexicana", 1024:"mexicana",
  1025:"mexicana", 1026:"mexicana", 1027:"mexicana", 1028:"mexicana",
  1029:"mexicana", 1030:"mexicana", 1031:"mexicana", 1032:"mexicana",
  1033:"mexicana", 1034:"internacional", 1035:"mexicana", 1036:"mexicana",
  1037:"mexicana", 1038:"mexicana", 1039:"internacional", 1040:"mexicana",
  1041:"mexicana", 1042:"mexicana", 1043:"mexicana", 1044:"mexicana",
  1045:"mexicana", 1046:"mexicana", 1047:"mexicana", 1048:"mexicana",
  1049:"mexicana", 1050:"mexicana", 1051:"mexicana", 1052:"mediterránea",
  1053:"mexicana", 1054:"mexicana", 1055:"mexicana", 1056:"mexicana",
  1057:"mexicana", 1058:"internacional", 1059:"internacional", 1060:"internacional",
  1061:"mexicana", 1062:"mexicana", 1063:"mexicana", 1064:"mexicana",
  1065:"mexicana", 1066:"mexicana", 1067:"mexicana", 1068:"internacional",
  1069:"mexicana", 1070:"mexicana", 1071:"mexicana", 1072:"mexicana",
  1073:"mexicana", 1074:"mexicana", 1075:"mexicana", 1076:"mexicana",
  1077:"internacional", 1078:"internacional", 1079:"mexicana", 1080:"internacional",
  1081:"internacional", 1082:"internacional", 1083:"mexicana", 1084:"mexicana",
  1085:"mexicana", 1086:"mexicana", 1087:"internacional", 1088:"mexicana",
  1089:"internacional", 1090:"mexicana", 1091:"mexicana", 1092:"mexicana",
  1093:"mexicana", 1094:"mexicana", 1095:"mexicana", 1096:"mexicana",
  1097:"italiana", 1098:"internacional", 1099:"fusion", 1100:"internacional",
  1101:"mexicana", 1102:"mexicana", 1103:"internacional", 1104:"mexicana",
  1105:"mexicana", 1106:"internacional", 1107:"mexicana", 1108:"mexicana",
  1109:"mexicana", 1110:"mexicana", 1111:"internacional", 1112:"internacional",
  1113:"mediterránea", 1114:"mexicana", 1115:"internacional", 1116:"mexicana",
  1117:"mexicana", 1118:"internacional", 1119:"española", 1120:"mexicana",
  1121:"asiática", 1122:"mexicana", 1123:"mexicana", 1124:"mexicana",
  1125:"mexicana", 1126:"mexicana", 1127:"internacional", 1128:"mexicana",
  1129:"mexicana", 1130:"mexicana", 1131:"internacional", 1132:"mexicana",
  1133:"mediterránea", 1134:"mexicana", 1135:"mexicana", 1136:"internacional",
  1137:"internacional", 1138:"mexicana", 1139:"internacional", 1140:"mexicana",
  1141:"asiática", 1142:"internacional", 1143:"mexicana", 1144:"internacional",
  1145:"mexicana", 1146:"mediterránea", 1147:"internacional", 1148:"mexicana",
  1149:"mexicana", 1150:"mexicana", 1151:"mexicana", 1152:"mediterránea",
  1153:"mexicana", 1154:"mexicana", 1155:"mexicana", 1156:"internacional",
  1157:"mexicana", 1158:"mexicana", 1159:"mexicana", 1160:"mexicana",
  1161:"italiana", 1162:"mexicana", 1163:"española", 1164:"mexicana",
  1165:"mexicana", 1166:"mediterránea", 1167:"mexicana", 1168:"internacional",
  1169:"internacional", 1170:"internacional", 1171:"internacional", 1172:"mexicana",
  1173:"mexicana", 1174:"mexicana", 1175:"mexicana", 1176:"mexicana",
  1177:"mexicana", 1178:"mexicana", 1179:"internacional", 1180:"mediterránea",
  1181:"mexicana", 1182:"mediterránea", 1183:"mexicana", 1184:"mexicana",
  1185:"mexicana", 1186:"internacional", 1187:"internacional", 1188:"mexicana",
  1189:"mexicana", 1190:"mediterránea", 1191:"internacional", 1192:"mexicana",
  1193:"internacional", 1194:"internacional", 1195:"mexicana", 1196:"internacional",
  1197:"mexicana", 1198:"mediterránea", 1199:"mexicana", 1200:"mexicana"
}

# Cambia "recetas.json" por el nombre exacto de tu archivo
with open("recetas.json", "r", encoding="utf-8") as f:
    recetas = json.load(f)

for receta in recetas:
    receta["tipo_cocina"] = tipo_cocina[receta["id"]]

with open("recetas.json", "w", encoding="utf-8") as f:
    json.dump(recetas, f, ensure_ascii=False, indent=2)

print(f"Listo! Se actualizaron {len(recetas)} recetas.")