import { TFile } from "obsidian";



export type ApparatusType = "FX" | "PH" | "SR" | "PB" | "HB"; // VT is not necessary
export type CategoryType = "Senior" | "Junior";

export type DifficultyValue = "A" | "B" | "C" | "D" | "E" | "F"| "G" | "H" | "I"; // DV
export type ElementGroup = "I" | "II" | "III" | "IV"; // EG

export type Type = "PROHIBITED_FOR_JUNIOR" | 
"FX_Multiple_salto_element" | "FX_Strength_element" | "FX_Circle_element" | "FX_Fwd_landing_element" | "FX_Bwd_landing_element" | "FX_Single_salto_element_without_turns" |
"PH_Handstand_element" | "PH_Spindle_element" | "PH_Sohn_element" | "PH_Bezugo_element" | "PH_Russian_element" | "PH_On_the_end_element" | "PH_Between_pommels_element" | "PH_Combined_element_without_russian" | "PH_Combined_element_with_russian" | "PH_Spindle_travel_element" | "PH_Cross_support_travel_element" | "PH_Russian_travel_element" |
"SR_Swing_to_handstand_element" | "SR_Swing_element" | "SR_Guczoghy_element" | "SR_L_sit_element" | "SR_V_sit_element" | "SR_Inverted_cross_element" | "SR_Hanging_scale_element" | "SR_Support_scale_element" | "SR_Swallow_element" | "SR_Inverted_swallow_element" | "SR_Cross_element" |
"PB_One_bar_element" | "PB_Upgraded_element" | "PB_Morisue_element" | "PB_Salto_fwd_straddled_element" | "PB_Salto_fwd_element" | "PB_Double_salto_fwd_element" | "PB_Dimitrenko_element" | "PB_Harada_element" | "PB_Pakhniuk_element" | "PB_Giant_swing_element" | "PB_Belle_element" | "PB_Torres_element" | "PB_Tanaka_element" | "PB_Basket_swing_element" | "PB_Gagnon_element" | "PB_Tejada_element" |
"HB_Swing_with_turn_element" | "HB_Rybalko_element" | "HB_Tkatchev_piatti_element" | "HB_Kovacs_element" | "HB_Stalder_rybalko_element" | "HB_Adler_element" | "HB_Adler_with_turn_element" | "HB_Quintero_element"


export enum EG {
    I = "I",
    II = "II",
    III = "III",
    IV = "IV"
}

export enum DV_SCORE {
    A = 0.1,
    B = 0.2,
    C = 0.3,
    D = 0.4,
    E = 0.5,
    F = 0.6,
    G = 0.7,
    H = 0.8,
    I = 0.9
}


// RESPONSE EXERCISE FROM THE DB
export interface ExerciseResponse {
    gymnastName: string;
    links: ElementResponse[]; // the first one is the gymnast !!
    frontmatter: FrontmatterResponse;
    exercisePath: string;
    file: TFile;
}

export interface ElementResponse {
    link: string; // path 
    displayText: string; // name
}

export interface FrontmatterResponse {
    Apparatus: ApparatusType;
    Category: CategoryType;

    D_Score?: number;
    CV?: number;

    // determine if the elements are connected
    "1+2": boolean;
    "2+3": boolean;
    "3+4": boolean;
    "4+5": boolean;
    "5+6": boolean;
    "6+7": boolean;
    "7+8": boolean;
    "8+9": boolean;
}


// RESPONSE ELEMENT FROM THE DB
export interface ElementFileResponse {
    frontmatter: ElementFileFrontmatterResponse;
}

export interface ElementFileFrontmatterResponse {
    Alias: string | null;
    Image: string;
    Symbol: string;
    Code: number;
    Apparatus: ApparatusType;
    EG: ElementGroup;
    DV: DifficultyValue;
    Type?: Type[];
    CV?: number; // connaction value
    D_Score?: number;
}

export interface Exercise {
    file: TFile;
    exercisePath: string;
    gymnastName: string;
    apparatus: ApparatusType;
    category: CategoryType;
    elements: Element[];
    connections: {
        "1+2": boolean;
        "2+3": boolean;
        "3+4": boolean;
        "4+5": boolean;
        "5+6": boolean;
        "6+7": boolean;
        "7+8": boolean;
        "8+9": boolean;
    },
    connectionsList: boolean[];
    score: number; // difficulty score ( with bonus )
    bonus: number; // connections values
    ND: number; // neutral deductions (warning)
}

export interface Element {
    id: string;
    index: number;
    elementPath: string;
    name: string;
    alias?: string;
    image?: string;
    apparatus: ApparatusType;
    EG: ElementGroup;
    DV: DifficultyValue;
    type?: Type[];
}

export interface MapExerciseResponse {
    exercise: Exercise,
    isValid: boolean;
}
