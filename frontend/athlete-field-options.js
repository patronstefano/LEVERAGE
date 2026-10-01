// Sporting country codes shared with the Gymternet normalization catalogue.
export const athleteCountryCodes = ["AFG","ALB","ALG","AND","ANG","ARG","ARM","ARU","AUS","AUT","AZE","BAN","BAR","BEL","BER","BIH","BIZ","BLR","BOL","BRA","BUL","CAM","CAN","CAY","CHA","CHI","CHN","CIV","CMR","COD","COL","CRC","CRO","CUB","CYP","CZE","DEN","DOM","ECU","EGY","ESA","ESP","EST","ETH","FAR","FIN","FRA","GBR","GEO","GER","GRE","GUA","HAI","HKG","HON","HUN","INA","IND","IRI","IRL","IRQ","ISL","ISR","ITA","JAM","JOR","JPN","KAZ","KGZ","KOR","KOS","KSA","KUW","LAT","LBA","LBN","LIE","LTU","LUX","MAR","MAS","MDA","MEX","MGL","MKD","MLI","MLT","MNE","MON","MRI","MYA","NAM","NCA","NED","NGR","NOR","NZL","PAK","PAN","PAR","PER","PHI","PLE","POL","POR","PRK","PUR","QAT","ROU","RSA","RUS","SCO","SEN","SEY","SGP","SLO","SRB","SRI","SUI","SVK","SWE","SYR","THA","TOG","TPE","TTO","TUN","TUR","UAE","UKR","URU","USA","UZB","VEN","VIE","YEM","ZIM"];

const countryRegions = {
  AFG:'AF', ALB:'AL', ALG:'DZ', AND:'AD', ANG:'AO', ARG:'AR', ARM:'AM', ARU:'AW', AUS:'AU', AUT:'AT', AZE:'AZ',
  BAN:'BD', BAR:'BB', BEL:'BE', BER:'BM', BIH:'BA', BIZ:'BZ', BLR:'BY', BOL:'BO', BRA:'BR', BUL:'BG', CAM:'KH',
  CAN:'CA', CAY:'KY', CHA:'TD', CHI:'CL', CHN:'CN', CIV:'CI', CMR:'CM', COD:'CD', COL:'CO', CRC:'CR', CRO:'HR',
  CUB:'CU', CYP:'CY', CZE:'CZ', DEN:'DK', DOM:'DO', ECU:'EC', EGY:'EG', ESA:'SV', ESP:'ES', EST:'EE', ETH:'ET',
  FAR:'FO', FIN:'FI', FRA:'FR', GBR:'GB', GEO:'GE', GER:'DE', GRE:'GR', GUA:'GT', HAI:'HT', HKG:'HK', HON:'HN',
  HUN:'HU', INA:'ID', IND:'IN', IRI:'IR', IRL:'IE', IRQ:'IQ', ISL:'IS', ISR:'IL', ITA:'IT', JAM:'JM', JOR:'JO',
  JPN:'JP', KAZ:'KZ', KGZ:'KG', KOR:'KR', KOS:'XK', KSA:'SA', KUW:'KW', LAT:'LV', LBA:'LY', LBN:'LB', LIE:'LI',
  LTU:'LT', LUX:'LU', MAR:'MA', MAS:'MY', MDA:'MD', MEX:'MX', MGL:'MN', MKD:'MK', MLI:'ML', MLT:'MT', MNE:'ME',
  MON:'MC', MRI:'MU', MYA:'MM', NAM:'NA', NCA:'NI', NED:'NL', NGR:'NG', NOR:'NO', NZL:'NZ', PAK:'PK', PAN:'PA',
  PAR:'PY', PER:'PE', PHI:'PH', PLE:'PS', POL:'PL', POR:'PT', PRK:'KP', PUR:'PR', QAT:'QA', ROU:'RO', RSA:'ZA',
  RUS:'RU', SEN:'SN', SEY:'SC', SGP:'SG', SLO:'SI', SRB:'RS', SRI:'LK', SUI:'CH', SVK:'SK', SWE:'SE', SYR:'SY',
  THA:'TH', TOG:'TG', TTO:'TT', TUN:'TN', TUR:'TR', UAE:'AE', UKR:'UA', URU:'UY', USA:'US', UZB:'UZ', VEN:'VE',
  VIE:'VN', YEM:'YE', ZIM:'ZW',
};
const sportingNames = {
  SCO: ['Scotland', 'Scozia', 'Escocia', 'Écosse'],
  TPE: ['Chinese Taipei', 'Taipei Cinese', 'Taipéi Chino', 'Taipei chinois'],
};

export function athleteFieldOptions(field, current = "", language = "en") {
  const value = String(current ?? "");
  const currentYear = new Date().getFullYear();
  const values = field === "country" ? [...athleteCountryCodes]
    : Array.from({ length: currentYear - 1899 }, (_, index) => String(currentYear - index));
  // Preserve official or historical values outside the suggested catalogue.
  if (value && !values.includes(value)) values.unshift(value);
  const locale = ['en', 'it', 'es', 'fr'].includes(language) ? language : 'en';
  const regions = field === 'country' ? new Intl.DisplayNames([locale], {type: 'region'}) : null;
  return [{ value: "", label: "—" }, ...values.map((item) => {
    const name = field === 'country' ? sportingNames[item]?.[['en', 'it', 'es', 'fr'].indexOf(locale)]
      || (countryRegions[item] ? regions.of(countryRegions[item]) : '') : '';
    return {value: item, label: name ? `${item} (${name})` : item};
  })];
}
