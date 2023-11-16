import { Exercise, ExerciseResponse } from "src/models";

export class Utils {
    static exerciseFolder = "MY DATA/My Exercises"; // name of the folder where the exercises are saved
    static noticeTimeout = 8000;
    
    static excersises: ExerciseResponse[] = [];
    static exerciseSelected: ExerciseResponse | undefined = undefined;

    static D_Score = 'D_Score';
    static CV_Score = 'CV';

}
