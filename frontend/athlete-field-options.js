// Sporting country codes shared with the Gymternet normalization catalogue.
export const athleteCountryCodes = ["AFG","ALB","ALG","AND","ANG","ARG","ARM","ARU","AUS","AUT","AZE","BAN","BAR","BEL","BER","BIH","BIZ","BLR","BOL","BRA","BUL","CAM","CAN","CAY","CHA","CHI","CHN","CIV","CMR","COD","COL","CRC","CRO","CUB","CYP","CZE","DEN","DOM","ECU","EGY","ESA","ESP","EST","ETH","FAR","FIN","FRA","GBR","GEO","GER","GRE","GUA","HAI","HKG","HON","HUN","INA","IND","IRI","IRL","IRQ","ISL","ISR","ITA","JAM","JOR","JPN","KAZ","KGZ","KOR","KOS","KSA","KUW","LAT","LBA","LBN","LIE","LTU","LUX","MAR","MAS","MDA","MEX","MGL","MKD","MLI","MLT","MNE","MON","MRI","MYA","NAM","NCA","NED","NGR","NOR","NZL","PAK","PAN","PAR","PER","PHI","PLE","POL","POR","PRK","PUR","QAT","ROU","RSA","RUS","SCO","SEN","SEY","SGP","SLO","SRB","SRI","SUI","SVK","SWE","SYR","THA","TOG","TPE","TTO","TUN","TUR","UAE","UKR","URU","USA","UZB","VEN","VIE","YEM","ZIM"];

export function athleteFieldOptions(field, current = "") {
  const value = String(current ?? "");
  const currentYear = new Date().getFullYear();
  const values = field === "country" ? [...athleteCountryCodes]
    : Array.from({ length: currentYear - 1899 }, (_, index) => String(currentYear - index));
  // Preserve official or historical values outside the suggested catalogue.
  if (value && !values.includes(value)) values.unshift(value);
  return [{ value: "", label: "—" }, ...values.map((item) => ({ value: item, label: item }))];
}
