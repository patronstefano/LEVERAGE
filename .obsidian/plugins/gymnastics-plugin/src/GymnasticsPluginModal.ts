import { Modal, App, Notice, TFile, TAbstractFile } from "obsidian";
import { strings } from "strings/strings";
import { ElementFileResponse, ElementResponse, Exercise, ExerciseResponse, Element, EG, MapExerciseResponse, DV_SCORE, FrontmatterResponse } from "./models";
import { Dropdown } from "./utils/dropdown";
import { Utils } from "./utils/utils";


export class GymnasticsPluginModal extends Modal {
	excercises: ExerciseResponse[];

	constructor(app: App) {
		super(app);
		this.getExercises();
	}

	onOpen() {
		const {contentEl} = this;
		const view = contentEl.createEl("div");
		view.createEl("h1", { text: strings.pluginName });
		view.createEl("h2", { text: strings.title });
        view.createEl("h4", { text: strings.chooseExercise });

		const elementsView = contentEl.createEl("div", { cls: "elementsContainer" });

		new Dropdown(contentEl, () => {
			if (!!Utils.exerciseSelected) {
				elementsView.empty();
				Utils.exerciseSelected.links.forEach((el: ElementResponse, index: number) => {
					if (index !== 0) {
						elementsView.createEl("p", { text: el.displayText, cls: "element" });
					}
				})
			}
		});

		const buttonView = contentEl.createEl("div");
        buttonView
			.createEl("button", { text: strings.check, cls: "checkButton" })
			.onClickEvent(() => {
				this.checkExercise();
			}
		);
	}

	onClose() {
		const {contentEl} = this;
		contentEl.empty();
	}

	getExercises() {
		const exercisesList: ExerciseResponse[] = [];
		const files = this.app.vault.getMarkdownFiles();

		files.forEach((el: any) => {
			if (el.path.includes(Utils.exerciseFolder)) {
				const exercise: ExerciseResponse = this.app.metadataCache.getFileCache(el) as unknown as ExerciseResponse;
				if (!!exercise && exercise.links?.length > 1) {
					exercise.gymnastName = exercise.links[0]?.displayText;
					exercise.file = el;
					exercise.exercisePath = el.path
					exercisesList.push(exercise);
				} else {
					new Notice(strings.noExerciseFound);
				}
			}
		});
		this.excercises = exercisesList;
		Utils.excersises = exercisesList;
	}

	mapExercise = (): MapExerciseResponse | undefined => {
        if (!!Utils.exerciseSelected) {

			const connectionsList: boolean[] = [];
			connectionsList.push(Utils.exerciseSelected.frontmatter["1+2"]);
			connectionsList.push(Utils.exerciseSelected.frontmatter["2+3"]);
			connectionsList.push(Utils.exerciseSelected.frontmatter["3+4"]);
			connectionsList.push(Utils.exerciseSelected.frontmatter["4+5"]);
			connectionsList.push(Utils.exerciseSelected.frontmatter["5+6"]);
			connectionsList.push(Utils.exerciseSelected.frontmatter["6+7"]);
			connectionsList.push(Utils.exerciseSelected.frontmatter["7+8"]);
			connectionsList.push(Utils.exerciseSelected.frontmatter["8+9"]);

            const exercise: Exercise = {
				file: Utils.exerciseSelected.file,
				exercisePath: Utils.exerciseSelected.exercisePath,
				gymnastName: Utils.exerciseSelected.links[0].displayText,
				apparatus: Utils.exerciseSelected.frontmatter.Apparatus,
				category: Utils.exerciseSelected.frontmatter.Category,
				elements: [],
				connections: {
					"1+2": Utils.exerciseSelected.frontmatter["1+2"],
					"2+3": Utils.exerciseSelected.frontmatter["2+3"],
					"3+4": Utils.exerciseSelected.frontmatter["3+4"],
					"4+5": Utils.exerciseSelected.frontmatter["4+5"],
					"5+6": Utils.exerciseSelected.frontmatter["5+6"],
					"6+7": Utils.exerciseSelected.frontmatter["6+7"],
					"7+8": Utils.exerciseSelected.frontmatter["7+8"],
					"8+9": Utils.exerciseSelected.frontmatter["8+9"]
				},
				connectionsList: connectionsList,
				score: 0.0,
				bonus: 0.0,
				ND: 0.0
			}

			const listOfCodes: string[] = []; // help to check if there is more than one element with the same code
			let isExerciseValid: boolean = true;

			Utils.exerciseSelected.links.forEach((el: ElementResponse, index: number) => {
				if (index !== 0) { // because in the first position there is the gymnast
					const element: ElementFileResponse = this.app.metadataCache.getCache(el.link) as unknown as ElementFileResponse;

					const elementMapped: Element = {
						id: element.frontmatter.EG + element.frontmatter.Code,
						elementPath: el.link,
						name: el.displayText,
						alias: element.frontmatter.Alias ?? '',
						image: element.frontmatter.Image,
						apparatus: element.frontmatter.Apparatus,
						EG: element.frontmatter.EG,
						DV: element.frontmatter.DV,
						type: element.frontmatter.Type,
						index: index
					}

					if (listOfCodes.includes(elementMapped.id)) {
						new Notice(strings.errorSameElement + ' Check: ' + elementMapped.name, Utils.noticeTimeout);
						isExerciseValid = false;
						return;
					} else {
						listOfCodes.push(elementMapped.id);
					}

					if (exercise.category === 'Junior' && elementMapped.type?.includes('PROHIBITED_FOR_JUNIOR')) {
						new Notice(strings.errorProhibitedElement + ' Check: ' + elementMapped.name, Utils.noticeTimeout);
						isExerciseValid = false;
						return;
					}
					
					if (exercise.apparatus !== element.frontmatter.Apparatus) {
						new Notice(strings.errorSameApparatus + ' Check: ' + elementMapped.name, Utils.noticeTimeout);
						isExerciseValid = false;
						return;
					}
	
					exercise.elements.push(elementMapped);
				}
			});
			return { exercise: exercise, isValid: isExerciseValid };

        } else {
            return undefined;
        }
    }

    async checkExercise() {
		if (!!Utils.exerciseSelected) {
			const exerciseMapped: MapExerciseResponse | undefined = this.mapExercise();

			if (exerciseMapped === undefined) {
				new Notice(strings.error, Utils.noticeTimeout);
				return;
			}
			let exerciseToCheck = exerciseMapped.exercise;
			let isExerciseValid: boolean = exerciseMapped.isValid;

			if ((exerciseToCheck.category === 'Junior' && exerciseToCheck.elements.length > 8)) {
				new Notice(strings.errorLongExercise, Utils.noticeTimeout);
				isExerciseValid = false;
			} else if ((exerciseToCheck.category === 'Junior' && exerciseToCheck.elements.length < 6) || (exerciseToCheck.category === 'Senior' && exerciseToCheck.elements.length < 8)) {
				new Notice(strings.errorShortExercise, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			let EGCount = [ 0, 0, 0, 0 ];
			exerciseToCheck.elements.forEach((el: Element) => {
				exerciseToCheck.score = exerciseToCheck.score + DV_SCORE[el.DV];
				switch (el.EG) {
					case EG.I: {
						EGCount[0] = EGCount[0] + 1;
						break;
					}
					case EG.II: {
						EGCount[1] = EGCount[1] + 1;
						break;
					}
					case EG.III: {
						EGCount[2] = EGCount[2] + 1;
						break;
					}
					case EG.IV: {
						EGCount[3] = EGCount[3] + 1;
						break;
					}
				}
			});

			if (EGCount[0] > 5 || EGCount[1] > 5 || EGCount[2] > 5) { // EG limits
				new Notice(strings.errorSameEG, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			if (EGCount[0] < 1 || EGCount[1] < 1 || EGCount[2] < 1) { // EG requirements (warning)
				new Notice(strings.warningMissingEG, Utils.noticeTimeout);
			}
			
			if (EGCount[0] > 0) { // EG1 (warning)
				exerciseToCheck.score = exerciseToCheck.score + 0.5;
			} else {
				new Notice(strings.warningEG1, Utils.noticeTimeout);
			}

			if (EGCount[1] > 0) { // EG2 (warning)
				if (EGCount[1] === 1 && exerciseToCheck.apparatus === 'FX' && exerciseToCheck.elements[exerciseToCheck.elements.length - 1].EG === 'II') { // Dismount FX (warning)
					new Notice(strings.warningFX_Dismount, Utils.noticeTimeout);
					new Notice(strings.warningEG2, Utils.noticeTimeout);
				} else {
					exerciseToCheck.score = exerciseToCheck.score + 0.5;
				}
			} else {
				new Notice(strings.warningEG2, Utils.noticeTimeout);
			}
			
			if (EGCount[2] > 0) { // EG3 (warning)
				if (EGCount[2] === 1 && exerciseToCheck.apparatus === 'FX' && exerciseToCheck.elements[exerciseToCheck.elements.length - 1].EG === 'III') { // Dismount FX (warning)
					new Notice(strings.warningFX_Dismount, Utils.noticeTimeout);
					new Notice(strings.warningEG3, Utils.noticeTimeout);
				} else {
					exerciseToCheck.score = exerciseToCheck.score + 0.5;
				}
			} else {
				new Notice(strings.warningEG3, Utils.noticeTimeout);
			}

			if (EGCount[3] > 1) { // Dismount limits
				new Notice(strings.errorDismount, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			if (EGCount[3] > 0 || exerciseToCheck.apparatus === 'FX') {  // Dismount requirement (warning)
				const dvDismount = exerciseToCheck.elements[exerciseToCheck.elements.length - 1].DV;
				if (exerciseToCheck.category === 'Junior') {
					if (dvDismount === 'B') {
						exerciseToCheck.score = exerciseToCheck.score + 0.3;
					} else if (dvDismount != 'A') {
						exerciseToCheck.score = exerciseToCheck.score + 0.5;
					}
				} else { // senior
					if (dvDismount === 'C') {
						exerciseToCheck.score = exerciseToCheck.score + 0.3;
					} else if (dvDismount !== 'A' && dvDismount !== 'B') {
						exerciseToCheck.score = exerciseToCheck.score + 0.5;
					}
				}
			} else {
				new Notice(strings.warningDismount, Utils.noticeTimeout);
			}

			if (exerciseToCheck.apparatus === "FX" && exerciseToCheck.elements[exerciseToCheck.elements.length - 1].EG === 'I') { // Dismount FX (error)
				new Notice(strings.errorFX_Dismount, Utils.noticeTimeout);
				isExerciseValid = false;
			} else if (exerciseToCheck.apparatus !== "FX" && exerciseToCheck.elements[exerciseToCheck.elements.length - 1].EG !== 'IV') {
				new Notice(strings.errorDismountEG, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			let exercise: Exercise = exerciseToCheck;
			
			if (exerciseToCheck.apparatus === 'FX') {
				const res = this.checkFX(exerciseToCheck, isExerciseValid);
				exercise = res.exercise;
				isExerciseValid = res.isExerciseValid;
			} else if (exerciseToCheck.apparatus === 'PH') {
				const res = this.checkPH(exerciseToCheck, isExerciseValid);
				exercise = res.exercise;
				isExerciseValid = res.isExerciseValid;
			} else if (exerciseToCheck.apparatus === 'SR') {
				const res = this.checkSR(exerciseToCheck, isExerciseValid);
				exercise = res.exercise;
				isExerciseValid = res.isExerciseValid;
			} else if (exerciseToCheck.apparatus === 'PB') {
				const res = this.checkPB(exerciseToCheck, isExerciseValid);
				exercise = res.exercise;
				isExerciseValid = res.isExerciseValid;
			} else if (exerciseToCheck.apparatus === 'HB') {
				const res = this.checkHB(exerciseToCheck, isExerciseValid);
				exercise = res.exercise;
				isExerciseValid = res.isExerciseValid;
			} 

			if (isExerciseValid) {
				new Notice(strings.noError, Utils.noticeTimeout);
				exercise.score = Math.round((exercise.score + exercise.bonus) * 100) / 100;
				exercise.bonus = Math.round(exercise.bonus * 100) / 100;
				exercise.ND = Math.round(exercise.ND * 100) / 100;

				const scoresWithND = 
					strings.difficultyScore + exercise.score + '\n (' +
					strings.connectionValues + exercise.bonus + ') \n' +
					strings.neutralDeductions + exercise.ND;

				const scoresWithoutND = 
					strings.difficultyScore + exercise.score + '\n (' +
					strings.connectionValues + exercise.bonus + ') \n';

				alert(exercise.ND > 0 ? scoresWithND : scoresWithoutND);

				const templateFile = this.app.vault.getAbstractFileByPath(exercise.exercisePath);

				if (templateFile instanceof TFile){
					const exerciseFile = await this.app.vault.cachedRead(templateFile);
					const lines = exerciseFile.split('\n');
					let modify: boolean = true;
					lines.forEach((el: string, index: number) => {
						if (el.contains(Utils.D_Score)) {
							const aux = el.split(': ');
							const newDScore = aux[0] + ': ' + exercise.score;
							if (parseFloat(aux[1]) === exercise.score) { // if same score do not modify file
								modify = false;
								return;
							}
							lines[index] = newDScore;
						} else if (el.contains(Utils.CV_Score)) {
							const aux = el.split(': ');
							const newDVScore = aux[0] + ': ' + exercise.bonus;
							if (!modify && parseFloat(aux[1]) === exercise.bonus) { // if same score do not modify file
								modify = false;
								return;
							} else {
								modify = true;
							}
							lines[index] = newDVScore;
						}
					})
				
					if (modify) {
						const newtext = lines.join('\n');
						const path = exercise.exercisePath;
						const indexTFile = this.app.vault.getAbstractFileByPath(exercise.exercisePath);
						if (indexTFile instanceof TAbstractFile) {
							this.app.vault.delete(indexTFile, true).then(async (value: any) => {
								await this.app.vault.create(path, newtext as unknown as string);
							});
						}
					}
				}	
			}

		} else {
			new Notice(strings.error, Utils.noticeTimeout);
		}
    }

	
	// FX
	checkFX(exercise: Exercise, isValid: boolean): {exercise: Exercise, isExerciseValid: boolean} {
		let isExerciseValid = isValid;

		let FX_Multiple_salto_element = 0; // min 1 (warning)
		let FX_Strength_element = 0; // max 2
		let FX_Circle_element = 0; // max 2
		exercise.elements.forEach((el: Element, index: number) => {
			el.type?.includes('FX_Multiple_salto_element') && (FX_Multiple_salto_element++);
			el.type?.includes('FX_Strength_element') && (FX_Strength_element++);
			el.type?.includes('FX_Circle_element') && (FX_Circle_element++);
		});

		if (FX_Multiple_salto_element === 0) {
			new Notice(strings.warningFX_MultipleSalto, Utils.noticeTimeout);
			exercise.ND = exercise.ND + 0.3;
		}

		if (FX_Strength_element > 2) {
			new Notice(strings.errorFX_StrenghtElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (FX_Circle_element > 2) {
			new Notice(strings.errorFX_CircleElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		exercise.connectionsList.forEach((isConnection: boolean, index: number) => {
			if (isConnection && exercise.elements.length >= (index + 2)) {
				const firstElement = index;
				const secondElement = index + 1;

				if (exercise.elements[firstElement].EG === 'I' || exercise.elements[secondElement].EG === 'I') {
					new Notice(strings.errorFX_Connection, Utils.noticeTimeout);
					isExerciseValid = false;
				} else if (exercise.elements[firstElement].type?.includes('FX_Fwd_landing_element') && !exercise.elements[firstElement].type?.includes('FX_Bwd_landing_element') && exercise.elements[secondElement].EG !== 'II') { // EG3
					new Notice(strings.errorFX_CounterSalto, Utils.noticeTimeout);
					isExerciseValid = false;
				} else if (exercise.elements[firstElement].type?.includes('FX_Bwd_landing_element') && !exercise.elements[firstElement].type?.includes('FX_Fwd_landing_element') && exercise.elements[secondElement].EG !== 'III') { // EG2
					new Notice(strings.errorFX_CounterSalto, Utils.noticeTimeout);
					isExerciseValid = false;
				} else if (!exercise.elements[firstElement].type?.includes('FX_Fwd_landing_element') && !exercise.elements[firstElement].type?.includes('FX_Bwd_landing_element')) {
					new Notice(strings.errorFX_Connection, Utils.noticeTimeout);
					isExerciseValid = false;
				} else if (!exercise.elements[firstElement].type?.includes('FX_Multiple_salto_element') && !exercise.elements[firstElement].type?.includes('FX_Single_salto_element_without_turns') && !exercise.elements[secondElement].type?.includes('FX_Multiple_salto_element') && !exercise.elements[secondElement].type?.includes('FX_Single_salto_element_without_turns')) {
					new Notice(strings.errorFX_ConnectionWithTurns, Utils.noticeTimeout);
					isExerciseValid = false;
				} else if (exercise.elements[firstElement].id === "II14" || exercise.elements[secondElement].id === "II14") { // II14 (Salto fwd. straight, also with 1⁄2 t.)
					new Notice(strings.warningFX_II14, Utils.noticeTimeout);
				}
	
				const DVfirstElement = exercise.elements[firstElement].DV;
				const DVsecondElement = exercise.elements[secondElement].DV;

				if (isExerciseValid) {
					if ((DVfirstElement !== 'A' && DVfirstElement !== 'B' && DVfirstElement !== 'C') && (DVsecondElement === 'B' || DVsecondElement === 'C')) {
						exercise.bonus = exercise.bonus + 0.1;
					} else if ((DVsecondElement !== 'A' && DVsecondElement !== 'B' && DVsecondElement !== 'C') && (DVfirstElement === 'B' || DVfirstElement === 'C')) {
						exercise.bonus = exercise.bonus + 0.1;
					} else if ((DVfirstElement !== 'A' && DVfirstElement !== 'B' && DVfirstElement !== 'C') && (DVsecondElement !== 'A' && DVsecondElement !== 'B' && DVsecondElement !== 'C')) {
						exercise.bonus = exercise.bonus + 0.2;
					}
				}
			}
		});
		return {exercise, isExerciseValid};		
	}


	// PH
	checkPH(exercise: Exercise, isValid: boolean): {exercise: Exercise, isExerciseValid: boolean} {
		let isExerciseValid = isValid;

		let PH_Combined_element_with_russian = 0; // max 1
		let PH_Combined_element_without_russian = 0; // max 1
		let PH_Handstand_element = 0; // max 2
		let PH_Russian_travel_element = 0; // max 2
		let PH_Cross_support_travel_element = 0; // max 2
		let PH_Spindle_travel_element = 0; // max 2
		let PH_Spindle_element = 0; // max 2
		let PH_Russian_element = 0; // max 2
		let PH_Sohn_element = 0; // max 2
		let PH_Bezugo_element = 0; // max 2

		let SohnAndBezugo = 0; // elements that has both Sohn and Bezugo Type

		const russianElements: Element[] = [];

		exercise.elements.forEach((el: Element, index: number) => {
			el.type?.includes('PH_Combined_element_with_russian') && (PH_Combined_element_with_russian++);
			el.type?.includes('PH_Combined_element_without_russian') && (PH_Combined_element_without_russian++);
			el.type?.includes('PH_Handstand_element') && (PH_Handstand_element++);
			el.type?.includes('PH_Russian_travel_element') && (PH_Russian_travel_element++);
			el.type?.includes('PH_Cross_support_travel_element') && (PH_Cross_support_travel_element++);
			el.type?.includes('PH_Spindle_travel_element') && (PH_Spindle_travel_element++);
			el.type?.includes('PH_Spindle_element') && (PH_Spindle_element++);
			el.type?.includes('PH_Russian_element') && (PH_Russian_element++);
			el.type?.includes('PH_Sohn_element') && (PH_Sohn_element++);
			el.type?.includes('PH_Bezugo_element') && (PH_Bezugo_element++);

			(el.type?.includes('PH_Bezugo_element') && el.type?.includes('PH_Sohn_element')) && (SohnAndBezugo++);

			if (el.type?.includes('PH_Russian_element')) {
				russianElements.push(el);
			}
		});

		if (PH_Combined_element_with_russian > 1) {
			new Notice(strings.errorPH_CombinedElementWithRussian, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PH_Combined_element_without_russian > 1) {
			new Notice(strings.errorPH_CombinedElementWithoutRussian, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PH_Handstand_element > 2) {
			new Notice(strings.errorPH_HandstandElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PH_Russian_travel_element > 2) {
			new Notice(strings.errorPH_RussianTravelElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PH_Cross_support_travel_element > 2) {
			new Notice(strings.errorPH_CrossSupportTravelElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PH_Spindle_travel_element > 2) {
			new Notice(strings.errorPH_SpindleTravelElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PH_Spindle_element > 2) {
			new Notice(strings.errorPH_SpindleElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PH_Russian_element > 2) {
			new Notice(strings.errorPH_RussianElement, Utils.noticeTimeout);
			isExerciseValid = false;
		} else if (PH_Russian_element === 2) {
			if (russianElements[0].type?.includes("PH_On_the_end_element") && russianElements[1].type?.includes("PH_On_the_end_element")) {
				new Notice(strings.errorPH_OnTheEndElement, Utils.noticeTimeout);
				isExerciseValid = false;
			} else if (russianElements[0].type?.includes("PH_Between_pommels_element") && russianElements[1].type?.includes("PH_Between_pommels_element")) {
				new Notice(strings.warningPH_BetweenPommelsElement, Utils.noticeTimeout);
			}
		}

		if (SohnAndBezugo === 0) {
			if (PH_Sohn_element > 2) {
				new Notice(strings.errorPH_SohnElement, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			if (PH_Bezugo_element > 2) {
				new Notice(strings.errorPH_BezugoElement, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		} else if (SohnAndBezugo === 1) {
			if (PH_Sohn_element > 3 || (PH_Sohn_element === 3 && PH_Bezugo_element === 3)) {
				new Notice(strings.errorPH_SohnElement, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			if (PH_Bezugo_element > 3 || (PH_Sohn_element === 3 && PH_Bezugo_element === 3)) {
				new Notice(strings.errorPH_BezugoElement, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		} else if (SohnAndBezugo === 2) {
			if (PH_Sohn_element > 4 || (PH_Sohn_element === 4 && PH_Bezugo_element >= 3)) {
				new Notice(strings.errorPH_SohnElement, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			if (PH_Bezugo_element > 4 || (PH_Sohn_element >= 3 && PH_Bezugo_element === 4)) {
				new Notice(strings.errorPH_BezugoElement, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		}
		return {exercise, isExerciseValid};		
	}


	// SR
	checkSR(exercise: Exercise, isValid: boolean): {exercise: Exercise, isExerciseValid: boolean} {
		let isExerciseValid = isValid;

		let SR_Swing_to_handstand_element = 0; // min 1 (warning)
		let SR_Swing_element = 0;
		let SR_Guczoghy_element = 0; // max 2
		let SR_Hanging_scale_element = 0; // max 1

		let LsitEG2 = 0; // max 1
		let LsitEG3 = 0; // max 1

		let VsitEG2 = 0; // max 1
		let VsitEG3 = 0; // max 1

		let CrossElementEG2 = 0; // max 1
		let CrossElementEG3 = 0; // max 1

		let InvertedCrossElementEG2 = 0; // max 1
		let InvertedCrossElementEG3 = 0; // max 1

		let InvertedSwallowElementEG2 = 0; // max 1
		let InvertedSwallowElementEG3 = 0; // max 1

		let SupportScaleElementEG3 = 0; // max 1
		let SupportScaleElementEG2 = 0; 

		let SwallowElementEG3 = 0; // max1
		let SwallowElementEG2 = 0; 

		let II65Element = 0;
		let II72Element = 0;

		exercise.elements.forEach((el: Element, index: number) => {
			el.type?.includes('SR_Swing_to_handstand_element') && (SR_Swing_to_handstand_element++);
			el.type?.includes('SR_Swing_element') && (SR_Swing_element++);
			el.type?.includes('SR_Guczoghy_element') && (SR_Guczoghy_element++);
			el.type?.includes('SR_Hanging_scale_element') && (SR_Hanging_scale_element++);

			(el.type?.includes('SR_L_sit_element') && el.EG === 'II') && (LsitEG2++);
			(el.type?.includes('SR_L_sit_element') && el.EG === 'III') && (LsitEG3++);

			(el.type?.includes('SR_V_sit_element') && el.EG === 'II') && (VsitEG2++);
			(el.type?.includes('SR_V_sit_element') && el.EG === 'III') && (VsitEG3++);

			(el.type?.includes('SR_Cross_element') && el.EG === 'II') && (CrossElementEG2++);
			(el.type?.includes('SR_Cross_element') && el.EG === 'III') && (CrossElementEG3++);

			(el.type?.includes('SR_Inverted_cross_element') && el.EG === 'II') && (InvertedCrossElementEG2++);
			(el.type?.includes('SR_Inverted_cross_element') && el.EG === 'III') && (InvertedCrossElementEG3++);

			(el.type?.includes('SR_Inverted_swallow_element') && el.EG === 'II') && (InvertedSwallowElementEG2++);
			(el.type?.includes('SR_Inverted_swallow_element') && el.EG === 'III') && (InvertedSwallowElementEG3++);

			(el.type?.includes('SR_Support_scale_element') && el.EG === 'III') && (SupportScaleElementEG3++);
			(el.type?.includes('SR_Support_scale_element') && el.EG === 'II') && (SupportScaleElementEG2++);

			(el.type?.includes('SR_Swallow_element') && el.EG === 'III') && (SwallowElementEG3++);
			(el.type?.includes('SR_Swallow_element') && el.EG === 'II') && (SwallowElementEG2++);

			(el.id === "II65") && (II65Element++);
			(el.id === "II72") && (II72Element++);
		});

		if (SR_Swing_to_handstand_element === 0) {
			new Notice(strings.warningSR_SwingToHandstandElement, Utils.noticeTimeout);
			exercise.ND = exercise.ND + 0.3;
		}

		if (SR_Guczoghy_element > 2) {
			new Notice(strings.errorSR_GuczoghyElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (SR_Hanging_scale_element > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_HangingScaleElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (LsitEG2 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_LsitEG2, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (LsitEG3 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_LsitEG3, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (VsitEG2 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_VsitEG2, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (VsitEG3 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_VsitEG3, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (CrossElementEG2 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_CrossElementEG2, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (CrossElementEG3 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_CrossElementEG3, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (InvertedCrossElementEG2 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_InvertedCrossElementEG2, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (InvertedCrossElementEG3 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_InvertedCrossElementEG3, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (InvertedSwallowElementEG2 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_InvertedSwallowElementEG2, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (InvertedSwallowElementEG3 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_InvertedSwallowElementEG3, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (SupportScaleElementEG3 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SupportScaleElementEG3, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (SwallowElementEG3 > 1) {
			new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SwallowElementEG3, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if ((II65Element === 1 && II72Element === 0) || (II65Element === 0 && II72Element === 1)) { // II65 (Van Gelder) && II72 (Zanetti)
			if (SwallowElementEG2 > 2 || (SwallowElementEG2 === 2 && SupportScaleElementEG2 === 2)) {
				new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SwallowElementEG2, Utils.noticeTimeout);
				isExerciseValid = false;
			}

			if (SupportScaleElementEG2 > 2 || (SwallowElementEG2 === 2 && SupportScaleElementEG2 === 2)) {
				new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SupportScaleElementEG2, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		} else if (II65Element === 1 && II72Element === 1) {
			if (SwallowElementEG2 > 2) {
				new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SwallowElementEG2, Utils.noticeTimeout);
				isExerciseValid = false;
			}
			if (SupportScaleElementEG2 > 2) {
				new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SupportScaleElementEG2, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		} else if (II65Element === 0 && II72Element === 0) {
			if (SwallowElementEG2 > 1) {
				new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SwallowElementEG2, Utils.noticeTimeout);
				isExerciseValid = false;
			}
			if (SupportScaleElementEG2 > 1) {
				new Notice(strings.errorSR_FinalStrenghtPosition + '\n' + strings.errorSR_SupportScaleElementEG2, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		}

		let counter: number = 0;

		exercise.elements.forEach((el: Element, index: number) => {
			if (el.type?.includes("SR_Swing_element") || el.EG === 'IV') {
				counter = 0;
			} else {
				counter++;
			}
			if (counter === 4) {
				new Notice(strings.errorSR_StrenghtSequence, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		});
		return {exercise, isExerciseValid};		
	}


	// PB
	checkPB(exercise: Exercise, isValid: boolean): {exercise: Exercise, isExerciseValid: boolean} {
		let isExerciseValid = isValid;

		let PB_Morisue_element = 0; // max 1
		let PB_Salto_fwd_straddled_element = 0; // max 1
		let PB_Salto_fwd_element = 0; // max 1
		let PB_Double_salto_fwd_element = 0; // max 1
		let PB_Dimitrenko_element = 0; // max 1
		let PB_Harada_element = 0; // max 1
		let PB_Pakhniuk_element = 0; // max 1
		let PB_Belle_element = 0; // max 1
		let PB_Torres_element = 0; // max 1
		let PB_Tanaka_element = 0; // max 1
		let PB_Gagnon_element = 0; // max 1
		let PB_Tejada_element = 0; // max 1

		let PB_Giant_swing_element = 0; // max 2
		let PB_Basket_swing_element = 0; // max 2

		let I69Element: undefined | number = undefined; // saving index 
		let I71Element: undefined | number = undefined; // saving index 

		exercise.elements.forEach((el: Element, index: number) => {
			el.type?.includes('PB_Morisue_element') && (PB_Morisue_element++);
			el.type?.includes('PB_Salto_fwd_straddled_element') && (PB_Salto_fwd_straddled_element++);
			el.type?.includes('PB_Salto_fwd_element') && (PB_Salto_fwd_element++);
			el.type?.includes('PB_Double_salto_fwd_element') && (PB_Double_salto_fwd_element++);
			el.type?.includes('PB_Dimitrenko_element') && (PB_Dimitrenko_element++);
			el.type?.includes('PB_Harada_element') && (PB_Harada_element++);
			el.type?.includes('PB_Pakhniuk_element') && (PB_Pakhniuk_element++);
			el.type?.includes('PB_Belle_element') && (PB_Belle_element++);
			el.type?.includes('PB_Torres_element') && (PB_Torres_element++);
			el.type?.includes('PB_Tanaka_element') && (PB_Tanaka_element++);
			el.type?.includes('PB_Gagnon_element') && (PB_Gagnon_element++);
			el.type?.includes('PB_Tejada_element') && (PB_Tejada_element++);
			el.type?.includes('PB_Giant_swing_element') && (PB_Giant_swing_element++);
			el.type?.includes('PB_Basket_swing_element') && (PB_Basket_swing_element++);

			(el.id === "I69") && (I69Element = index);
			(el.id === "I71") && (I71Element = index);
		});

		if (PB_Morisue_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_MorisueElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Salto_fwd_straddled_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_SaltoFwdStraddledElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Salto_fwd_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_SaltoFwdElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Double_salto_fwd_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_DoubleSaltoFwdElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Dimitrenko_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_DimitrenkoElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Harada_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_HaradaElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Pakhniuk_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_PakhniukElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Belle_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_BelleElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Torres_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_TorresElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Tanaka_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_TanakaElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Gagnon_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_GagnonElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Tejada_element > 1) {
			new Notice(strings.errorPB_SaltoElement + '\n' + strings.errorPB_TejadaElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Giant_swing_element > 2) {
			new Notice(strings.errorPB_GiantSwingElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (PB_Basket_swing_element > 2) {
			new Notice(strings.errorPB_BasketSwingElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (!!I69Element || !!I71Element) { // I69 (Bejenaru to upper arm hang) && I71 (Bejenaru)
			if (!!I69Element && !exercise.elements[I69Element - 1].type?.includes('PB_One_bar_element')) {
				new Notice(strings.errorPB_OneBarElementI69, Utils.noticeTimeout);
				isExerciseValid = false;
			} else if (!!I69Element && !exercise.elements[I69Element - 1].type?.includes('PB_Upgraded_element')) {
				new Notice(strings.errorPB_UpgradedElementI69, Utils.noticeTimeout);
				isExerciseValid = false;
			}
			if (!!I71Element && !exercise.elements[I71Element - 1].type?.includes('PB_One_bar_element')) {
				new Notice(strings.errorPB_OneBarElementI71, Utils.noticeTimeout);
				isExerciseValid = false;
			} else if (!!I71Element && !exercise.elements[I71Element - 1].type?.includes('PB_Upgraded_element')) {
				new Notice(strings.errorPB_UpgradedElementI71, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		}

		exercise.elements.forEach((el: Element, index: number) => {
			if (el.type?.includes('PB_Upgraded_element') && exercise.elements.length > (index + 1)) {
				if (exercise.elements[index + 1].id !== 'I69' && exercise.elements[index + 1].id !== 'I71') {
					new Notice(strings.errorPB_UpgradedElement, Utils.noticeTimeout);
					isExerciseValid = false;
			 	}
			}	
		});
		return {exercise, isExerciseValid};		
	}


	// HB
	checkHB(exercise: Exercise, isValid: boolean): {exercise: Exercise, isExerciseValid: boolean} {
		let isExerciseValid = isValid;

		let HB_Swing_with_turn_element = 0; // max 1
		let HB_Rybalko_element = 0; // max 1
		let HB_Stalder_rybalko_element = 0; // max 1
		let HB_Adler_with_turn_element = 0; // max 1
		let HB_Quintero_element = 0; // max 1

		let HB_Adler_element = 0 // max 2

		let HB_Tkatchev_piatti_element = 0;
		let HB_Kovacs_element = 0;

		exercise.elements.forEach((el: Element, index: number) => {
			el.type?.includes('HB_Swing_with_turn_element') && (HB_Swing_with_turn_element++);
			el.type?.includes('HB_Rybalko_element') && (HB_Rybalko_element++);
			el.type?.includes('HB_Stalder_rybalko_element') && (HB_Stalder_rybalko_element++);
			el.type?.includes('HB_Adler_with_turn_element') && (HB_Adler_with_turn_element++);
			el.type?.includes('HB_Quintero_element') && (HB_Quintero_element++);
			el.type?.includes('HB_Adler_element') && (HB_Adler_element++);
			el.type?.includes('HB_Tkatchev_piatti_element') && (HB_Tkatchev_piatti_element++);
			el.type?.includes('HB_Kovacs_element') && (HB_Kovacs_element++);
		});

		if (HB_Swing_with_turn_element > 1) {
			new Notice(strings.errorHB_TurnElement + '\n' + strings.errorHB_SwingWithTurnElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (HB_Rybalko_element > 1) {
			new Notice(strings.errorHB_TurnElement + '\n' + strings.errorHB_RybalkoElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (HB_Stalder_rybalko_element > 1) {
			new Notice(strings.errorHB_TurnElement + '\n' + strings.errorHB_StalderRybalkoElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (HB_Adler_with_turn_element > 1) {
			new Notice(strings.errorHB_TurnElement + '\n' + strings.errorHB_AdlerWithTurnElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (HB_Quintero_element > 1) {
			new Notice(strings.errorHB_TurnElement + '\n' + strings.errorHB_QuinteroElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (HB_Adler_element > 2) {
			new Notice(strings.errorHB_AdlerElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		let is_HB_Tkatchev_piatti_Connection_Valid = false;
		let is_HB_Kovacs_Connection_Valid = false;

		if (exercise.connectionsList.includes(true)) {
			exercise.connectionsList.forEach((isConnection: boolean, index: number) => {
				if (isConnection && exercise.elements.length >= (index + 2)) {
					const firstElement = index;
					const secondElement = index + 1;

					if ((exercise.elements[firstElement].EG !== "II" || !exercise.elements[firstElement].type?.includes('HB_Adler_element')) && exercise.elements[secondElement].EG !== "II") {
						new Notice(strings.errorHB_Connection, Utils.noticeTimeout);
						isExerciseValid = false;
					} else if (!exercise.elements[firstElement].type?.includes('HB_Adler_element') && !exercise.elements[secondElement].type?.includes('HB_Adler_element')) {
						if (exercise.elements[firstElement].type?.includes("HB_Tkatchev_piatti_element") || exercise.elements[secondElement].type?.includes("HB_Tkatchev_piatti_element")) {
							is_HB_Tkatchev_piatti_Connection_Valid = true;
						}
						if (exercise.elements[firstElement].type?.includes("HB_Kovacs_element") || exercise.elements[secondElement].type?.includes("HB_Kovacs_element")) {
							is_HB_Kovacs_Connection_Valid = true;
						}
					}

					const DVfirstElement = exercise.elements[firstElement].DV;
					const DVsecondElement = exercise.elements[secondElement].DV;

					if (isExerciseValid) {
						if (exercise.elements[firstElement].EG === "II" && exercise.elements[secondElement].EG === "II") {
							if ((DVfirstElement === 'C') && (DVsecondElement !== 'A' && DVsecondElement !== 'B')) {
								exercise.bonus = exercise.bonus + 0.1;
							} else if ((DVsecondElement === 'C') && (DVfirstElement !== 'A' && DVfirstElement !== 'B')) {
								exercise.bonus = exercise.bonus + 0.1;
							} else if ((DVfirstElement !== 'A' && DVfirstElement !== 'B' && DVfirstElement !== 'C') && (DVsecondElement !== 'A' && DVsecondElement !== 'B' && DVsecondElement !== 'C')) {
								exercise.bonus = exercise.bonus + 0.2;
							}
						} else if (exercise.elements[firstElement].type?.includes('HB_Adler_element') && exercise.elements[secondElement].EG === "II") {
							if (DVfirstElement !== 'A' && DVfirstElement !== 'B' && DVfirstElement !== 'C') {
								if (DVsecondElement === 'D') {
									exercise.bonus = exercise.bonus + 0.1;
								} else if (DVsecondElement !== 'A' && DVsecondElement !== 'B' && DVsecondElement !== 'C') {
									exercise.bonus = exercise.bonus + 0.2;	
								}
							}
						}
					}
				}
			});
		}
		
		if (is_HB_Tkatchev_piatti_Connection_Valid) {
			if (HB_Tkatchev_piatti_element > 3) {
				new Notice(strings.errorHB_TkatchevPiattiElementConnected, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		} else if (HB_Tkatchev_piatti_element > 2) {
			new Notice(strings.errorHB_TkatchevPiattiElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}

		if (is_HB_Kovacs_Connection_Valid) {
			if (HB_Kovacs_element > 3) {
				new Notice(strings.errorHB_KovacsElementConnected, Utils.noticeTimeout);
				isExerciseValid = false;
			}
		} else if (HB_Kovacs_element > 2) {
			new Notice(strings.errorHB_KovacsElement, Utils.noticeTimeout);
			isExerciseValid = false;
		}
		
		return {exercise, isExerciseValid};		
	}
}
