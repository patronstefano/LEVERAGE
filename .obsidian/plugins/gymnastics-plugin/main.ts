import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting, TFile } from 'obsidian';
import { strings } from 'strings/strings';
import { GymnasticsPluginModal } from 'src/GymnasticsPluginModal';


interface GymnasticsPluginSettings {
	setting: string;
}

const DEFAULT_SETTINGS: GymnasticsPluginSettings = {
	setting: ''
}

export default class MyPlugin extends Plugin {
	settings: GymnasticsPluginSettings;

	async onload() {
		await this.loadSettings();

		// This creates an icon in the left ribbon
		const ribbonIconEl = this.addRibbonIcon(strings.iconSymbol, strings.iconName, (evt: MouseEvent) => {
			new GymnasticsPluginModal(this.app).open();
		});
		// Perform additional things with the ribbon
		ribbonIconEl.addClass(strings.iconClass);

		// This adds a status bar item to the bottom of the app
		const statusBarItemEl = this.addStatusBarItem();
		statusBarItemEl.setText(strings.barName);
		
		// This adds a simple command that can be triggered anywhere
		this.addCommand({
			id: strings.commandId,
			name: strings.commandName,
			callback: () => {
				new GymnasticsModal(this.app).open();
			}
		});

		// This adds a settings tab so the user can configure various aspects of the plugin
		this.addSettingTab(new GymnasticsSetting(this.app, this));
	}

	onunload() {
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}

class GymnasticsModal extends Modal {
	constructor(app: App) {
		super(app);
	}

	onOpen() {
		const {contentEl} = this;
		const view = contentEl.createEl("div");
		view.createEl("h1", {text: strings.contentName});
		view.createEl("p", {text: strings.contentText1});
		view.createEl("p", {text: strings.contentText2});
		view.createEl("p", {text: strings.contentText3});
		view.createEl("p", {text: strings.contentText4});
		view.createEl("p", {text: strings.contentText5});
	}

	onClose() {
		const {contentEl} = this;
		contentEl.empty();
	}
}

class GymnasticsSetting extends PluginSettingTab {
	plugin: MyPlugin;

	constructor(app: App, plugin: MyPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const {containerEl} = this;

		containerEl.empty();
		containerEl.createEl('h1', {text: strings.containerText});

		new Setting(containerEl)
			.setName(strings.settingName)
			.setDesc(strings.settingDesc)
			.addText(text => text
				.setPlaceholder(strings.settingText)
				.setValue(this.plugin.settings.setting)
				.onChange(async (value) => {
					this.plugin.settings.setting = value;
					await this.plugin.saveSettings();
				}));
	}
}
