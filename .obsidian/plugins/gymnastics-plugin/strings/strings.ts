export const strings = {
    
    //Main
    iconSymbol: "check-circle",
    iconName: "Check a gymnastics exercise",
    iconClass: "GymnasticsPlugin",

    barName: "Gymnastics Bar Text",

    commandId: "open-gymnastics-modal-simple",
    commandName: "Open the User Guide for Gymnastics Plugin",

    contentName: "User Guide for Gymnastics Plugin",
    contentText1: "1. Click on the check-circle button 'Check a gymnastics exercise' included in the Ribbon.",
    contentText2: "2. Choose the exercise you want to check (a preview of the elements of the exercise selected is displayed).",
    contentText3: "3. Click on 'Check':",
    contentText4: "- If the exercise is not correct, a notice is displayed to report the composition errors committed in the exercise analyzed.",
    contentText5: "- If the exercise is correct, a notice of correct composition is displayed and the Difficulty Score (D Score) of the exercise is calculated. D Score with Connection Values (CV) (and also possible Neutral Deductions (ND) of composition) of the exercise are displayed and automatically included in the Metadata (YAML) of the file of the exercise analyzed.",

    containerText: "Settings for Gymnastics Plugin",
    
    settingName: "Language",
    settingDesc: "English",
    settingText: "Enter your language",
    
    //GymnasticsPluginModal
    pluginName: "Gymnastics Plugin",
    title: "Check a gymnastics exercise and calculate its Difficulty Score",
    chooseExercise: "Exercise selected:",
    check: "Check",

    noExerciseFound: "No exercise found",
    noError: "The exercise is correct",
    error: "The exercise is not valid",

    errorSameElement: "An element (or elements with the same Code Identification Number) cannot be repeated for difficulty credit to D Score.",
    errorProhibitedElement: "Junior gymnasts cannot perform prohibited elements (not permitted in Junior category) in their exercise.",
    errorSameApparatus: "All elements must belong to the same apparatus included in the exercise.",
    
    errorLongExercise: "Junior gymnasts cannot perform more than 8 counting elements in their exercise.",
    errorShortExercise: "Performing less than 8 elements in Senior category (6 in Junior category) involves an appropriate Neutral Deduction (ND) for a short exercise.",
    
    errorSameEG: "It is not possibile to perform more than 5 elements from the same Element Group (for FX, the Element Group of the dismount will count first).",
    warningMissingEG: "At least one element from each Element Group must be included in the execise to fulfill Element Group requirement.",
    warningEG1: "Element Group I requirement is not fulfilled.",
    warningEG2: "Element Group II requirement is not fulfilled.",
    warningEG3: "Element Group III requirement is not fulfilled.",
    
    errorDismount: "It is not possibile to perform more than 1 dismount.",
    errorDismountEG: "The dismount must be from Element Group IV (except for FX).",
    warningDismount: "Dismount Element Group requirement is not fulfilled.",

    difficultyScore: "D SCORE: ",
    connectionValues: "CV: ",
    neutralDeductions: "ND: ",
    
    //FX
    warningFX_Dismount: "The element from Element Group II or III (executed as dismount on FX) can fulfill only the Dismount Group requirement. This element is the first of the five counted within its Element Group and one more element from the same Element Group must be included inside the exercise in order to fulfill this Element Group requirement.",
    errorFX_Dismount: "The dismount cannot be from Element Group I.",

    warningFX_MultipleSalto: "A multiple salto element is required in the exercise and must be inside the 10 (8 in Junior category) counting elements.",
    errorFX_StrenghtElement: "A maximum of 2 strength elements (including strength handstands) may be performed in an exercise for content value.",
    errorFX_CircleElement: "A maximum of 2 circle, flair or Russian elements may be performed in an exercise for difficulty value.",
    errorFX_CounterSalto: "No connection bonus will be given for counter saltos.",
    errorFX_Connection: "Connection between elements not valid.",
    errorFX_ConnectionWithTurns: "No connection bonus will be given for directly connected single saltos with turns.",
    warningFX_II14: "Connection bonus will be given ONLY for connections to Salto fwd. straight WITHOUT 1/2 t. (EG II.14).",

    //PH
    errorPH_CombinedElementWithRussian: "A maximum of 1 combined sequence on a single pommel with Russian Wendeswings is permitted for value in an exercise.",
    errorPH_CombinedElementWithoutRussian: "A maximum of 1 combined sequence on a single pommel without Russian Wendeswings is permitted for value in an exercise.",
    errorPH_HandstandElement: "A maximum of 2 handstand elements are permitted for value in an exercise from circles, flairs, or scissors (not including the dismount).",
    errorPH_RussianTravelElement: "A maximum of 2 Russian Wendeswings travel elements are permitted for value in an exercise.",
    errorPH_CrossSupportTravelElement: "A maximum of 2 cross support travels (forwards and/or backwards) are permitted during the exercise.",
    errorPH_SpindleTravelElement: "A maximum of 2 travel with Spindle elements are permitted for value in an exercise.",
    errorPH_SpindleElement: "A maximum of 2 full Spindle elements are permitted for value in an exercise.",
    errorPH_RussianElement: "A maximum of 2 Russian Wendeswings are permitted for value in an exercise, including the dismount.",
    errorPH_OnTheEndElement: "Any second Russian Wenderswing element ON THE END (including dismount) is considered as repetition.",
    warningPH_BetweenPommelsElement: "Any second Russian Wenderswing element BETWEEN POMMELS is considered as repetition. At least one of them must be performed ON A SINGLE POMMEL.",
    errorPH_SohnElement: "A maximum of 2 Sohn type elements are permitted for value in an exercise, including combined and handstands.",
    errorPH_BezugoElement: "A maximum of 2 Bezugo type elements are permitted for value in an exercise, including combined and handstands.",

    //SR
    warningSR_SwingToHandstandElement: "A Swing to handstand element (2 s. hold) is required in the exercise and must be inside the 10 (8 in Junior category) counting elements.",
    errorSR_GuczoghyElement: "A maximum of 2 Guczoghy type elements can be presented in the exercise.",
    errorSR_FinalStrenghtPosition: "A maximum of 1 final strength position in each EG may be recognized for difficulty.",
    errorSR_HangingScaleElement: "Too many Hanging Scale type elements.",
    errorSR_LsitEG2: "Too many L sit type elements from EG II.",
    errorSR_LsitEG3: "Too many L sit type elements from EG III.",
    errorSR_VsitEG2: "Too many V sit type elements from EG II.",
    errorSR_VsitEG3: "Too many V sit type elements from EG III.",
    errorSR_CrossElementEG2: "Too many Cross type elements from EG II.",
    errorSR_CrossElementEG3: "Too many Cross type elements from EG III.",
    errorSR_InvertedCrossElementEG2: "Too many Inverted Cross type elements from EG II.",
    errorSR_InvertedCrossElementEG3: "Too many Inverted Cross type elements from EG III.",
    errorSR_InvertedSwallowElementEG2: "Too many Inverted Swallow type elements from EG II.",
    errorSR_InvertedSwallowElementEG3: "Too many Inverted Swallow type elements from EG III.",
    errorSR_SwallowElementEG2: "Too many Swallow type elements from EG II.",
    errorSR_SwallowElementEG3: "Too many Swallow type elements from EG III.",
    errorSR_SupportScaleElementEG2: "Too many Support Scale type elements from EG II.",
    errorSR_SupportScaleElementEG3: "Too many Support Scale type elements from EG III.",
    errorSR_StrenghtSequence: "A maximum of 3 elements from EG II and/or EG III can be presented in direct succession. The following element must be a B value Swing element from EG I (except any kind of kip/back kip, or element in the same Code box).",

    //PB
    errorPB_SaltoElement: "An exercise cannot include more than 1 body/regrasp position variation of the same element with salto (within the same EG).",
    errorPB_MorisueElement: "Too many Morisue type elements.",
    errorPB_SaltoFwdStraddledElement: "Too many Salto Fwd Straddled type elements.",
    errorPB_SaltoFwdElement: "Too many Salto Fwd type elements.",
    errorPB_DoubleSaltoFwdElement: "Too many Double Salto Fwd type elements.",
    errorPB_DimitrenkoElement: "Too many Dimitrenko type elements.",
    errorPB_HaradaElement: "Too many Harada type elements.",
    errorPB_PakhniukElement: "Too many Pakhniuk type elements.",
    errorPB_BelleElement: "Too many Belle type elements.",
    errorPB_TorresElement: "Too many Torres type elements.",
    errorPB_TanakaElement: "Too many Tanaka type elements.",
    errorPB_GagnonElement: "Too many Gagnon type elements.",
    errorPB_TejadaElement: "Too many Tejada type elements.",
    errorPB_GiantSwingElement: "A maximum of 2 Giant Swings through handstand are permitted for value in an exercise.",
    errorPB_BasketSwingElement: "A maximum of 2 Basket Swings through handstand are permitted for value in an exercise.",
    errorPB_OneBarElementI69: "Bejenaru to upper arm hang (EG I.69) must follow a swing element (min. B) to hdst on 1 rail.",
    errorPB_OneBarElementI71: "Bejenaru (EG I.71) must follow a swing element (min. B) to hdst on 1 rail.",
    errorPB_UpgradedElementI69: "The swing element followed by Bejenaru to upper arm hang (EG I.69) is not valid. Only swing elements CONNECTED TO HEALY TYPE ELEMENT are permitted.",
    errorPB_UpgradedElementI71: "The swing element followed by Bejenaru (EG I.71) is not valid. Only swing elements CONNECTED TO HEALY TYPE ELEMENT are permitted.",
    errorPB_UpgradedElement: "Swing elements CONNECTED TO HEALY TYPE ELEMENT must be followed by Bejenaru to upper arm hang (EG I.69) or Bejenaru (EG I.71).",

    //HB
    errorHB_TurnElement: "An exercise cannot include more than 1 grip variation of the same element with turn.",
    errorHB_SwingWithTurnElement: "Too many Swing With Turn type elements.",
	errorHB_RybalkoElement: "Too many Rybalko type elements.",
	errorHB_StalderRybalkoElement: "Too many Stalder Rybalko type elements.",
	errorHB_AdlerWithTurnElement: "Too many Adler With Turn type elements.",
	errorHB_QuinteroElement: "Too many Quintero type elements.",
    errorHB_AdlerElement: "A maximum of 2 Stoop Circle Rearward forward through handstand (Adler type) elements are permitted for value in an exercise.",
    errorHB_TkatchevPiattiElement: "A maximum of 2 Tkatchev or Piatti style flight elements are permitted for value in an exercise (3 are only permitted if one is directly connected to any style release).",
    errorHB_TkatchevPiattiElementConnected: "A maximum of 3 Tkatchev or Piatti style flight elements are permitted for value in an exercise (only if one is directly connected to any style release).",
    errorHB_KovacsElement: "A maximum of 2 Kovacs style flight elements are permitted for value in an exercise (3 are only permitted if one is directly connected to any style release).", 
    errorHB_KovacsElementConnected: "A maximum of 3 Kovacs style flight elements are permitted for value in an exercise (only if one is directly connected to any style release).",
    errorHB_Connection: "Connection between elements not valid.",
}
