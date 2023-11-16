import { DropdownComponent, App } from "obsidian";
import { Exercise, ExerciseResponse } from "src/models";
import { Utils } from "./utils";

export class Dropdown extends DropdownComponent {
    selectEl: HTMLSelectElement

	constructor(containerEl: HTMLElement, callback: () => void) {
		super(containerEl);
        
        Utils.excersises.forEach((el: ExerciseResponse, index: number) => {
            const path = el.exercisePath.split('/');
            this.addOption(index.toString(), path[path.length - 1]);       
        });
        
        if (Utils.excersises.length > 0) {
            Utils.exerciseSelected = Utils.excersises[0];
            callback();
        }

        this.onChange((value: string) => {
            Utils.exerciseSelected = Utils.excersises[parseInt(value)];
            callback();
        });  
	}
}
