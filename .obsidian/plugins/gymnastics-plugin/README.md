# Gymnastics Plugin

This is a plugin for gymnastics users of Obsidian (https://obsidian.md).

This plugin checks the correct composition of a gymnastics exercise and calculates its Difficulty Score, in accordance with the rules of the 2022-2024 Code of Points of Men’s Artistic Gymnastics.

It is a custom add-in for LEVERAGE, a software developed to support the management of complexity in Artistic Gymnastics and released freely by Patron Stefano - Uninettuno International Telematic University, Faculty of Engineering, Rome, Italy.

**Note: this plugin needs LEVERAGE to work.**

## Installation
This plugin is directly included in LEVERAGE.

## Usage
1. Click on the check-circle button "Check a gymnastics exercise" included in the Ribbon.
2. Choose the exercise you want to check (a preview of the elements of the exercise selected is displayed).
3. Click on "Check":
    - If the exercise is not correct, a notice is displayed to report the composition errors committed in the exercise analyzed.
    - If the exercise is correct, a notice of correct composition is displayed and the Difficulty Score (D Score) of the exercise is calculated. D Score with Connection Values (CV) (and also possible Neutral Deductions (ND) of composition) of the exercise are displayed and automatically included in the Metadata (YAML) of the file of the exercise analyzed.

**Note: the creation of new files of exercises or their update/deletion is possibile through the "Exercise DB" (included in LEVERAGE). This tool provides a valid file format of exercises for the correct working of the plugin.**

**Note: the exercises selectable through the plugin are included in the "MY DATA/My Exercises" folder (included in LEVERAGE), where all exercises dysplayed in the "Exercise DB" are saved.**

## Demo
![](DEMO.mov)

## Hotkeys
This plugin includes its own hotkey, that directly opens the User Guide of the plugin.
The hotkey is defined as default keyboards commands:
⌘+X (CTRL+X)

## Settings
This plugin only supports English language, that is setted as default.

--- 

<div align="center">
MIT licensed | Copyright © 2023 Stefano Patron
</div>
