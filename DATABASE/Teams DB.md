---
database-plugin: basic
FX_Final_Score: NaN
PH_Final_Score: NaN
SR_Final_Score: NaN
VT_Final_Score: NaN
HB_Final_Score: NaN
AA_Final_Score: NaN
PB_Final_Score: NaN
AA_D_Score: NaN
---

```yaml:dbfolder
name: Teams DB
description: Database of Teams
columns:
  __file__:
    key: __file__
    id: __file__
    input: markdown
    label: File
    accessorKey: __file__
    isMetadata: true
    skipPersist: false
    isDragDisabled: false
    csvCandidate: true
    position: 1
    isHidden: false
    sortIndex: -1
    width: 207
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      footer_formula: 
      wrap_content: true
  Alias:
    input: select
    accessorKey: Alias
    key: Alias
    id: Alias
    label: Team
    position: 2
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 201
    options:
      - { label: "Spes Mestre ASD", value: "Spes Mestre ASD", color: "hsl(163, 95%, 90%)"}
      - { label: "La Marmora Biella ASD", value: "La Marmora Biella ASD", color: "hsl(0,93%,88%)"}
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      option_source: manual
  Championship:
    input: select
    accessorKey: Championship
    key: Championship
    id: Championship
    label: Championship
    position: 3
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 174
    options:
      - { label: "Serie A1", value: "Serie A1", color: "hsl(228,100%,62%)"}
      - { label: "Serie A2", value: "Serie A2", color: "hsl(225,100%,84%)"}
      - { label: "Serie B", value: "Serie B", color: "hsl(198,100%,80%)"}
      - { label: "Serie C", value: "Serie C", color: "hsl(181,93%,88%)"}
      - { label: "1.Bundesliga", value: "1.Bundesliga", color: "hsl(1,100%,70%)"}
      - { label: "2.Bundesliga", value: "2.Bundesliga", color: "hsl(38,100%,70%)"}
      - { label: "3.Bundesliga", value: "3.Bundesliga", color: "hsl(67,100%,74%)"}
      - { label: "Top 12", value: "Top 12", color: "hsl(107,100%,63%)"}
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      option_source: manual
  Country:
    input: select
    accessorKey: Country
    key: Country
    id: Country
    label: Country
    position: 4
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 169
    options:
      - { label: "Italy", value: "Italy", color: "hsl(206,100%,65%)"}
      - { label: "France", value: "France", color: "hsl(118,100%,74%)"}
      - { label: "Germany", value: "Germany", color: "hsl(0,100%,72%)"}
      - { label: "Spain", value: "Spain", color: "hsl(55,100%,80%)"}
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      option_source: manual
  Gymnasts:
    input: relation
    accessorKey: Gymnasts
    key: Gymnasts
    id: Gymnasts
    label: Gymnasts
    position: 7
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 223
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      relation_color: hsl(0,0%,0%)
      related_note_path: DATABASE/Gymnasts DB.md
      bidirectional_relation: true
config:
  remove_field_when_delete_column: false
  cell_size: normal
  sticky_first_column: true
  group_folder_column: 
  remove_empty_folders: false
  automatically_group_files: false
  hoist_files_with_empty_attributes: false
  show_metadata_created: false
  show_metadata_modified: false
  show_metadata_tasks: false
  show_metadata_inlinks: false
  show_metadata_outlinks: false
  source_data: tag
  source_form_result: "#TEAM"
  source_destination_path: MY DATA/My Teams
  row_templates_folder: /
  current_row_template: DATABASE/TEMPLATES/New Team.md
  pagination_size: 200
  font_size: 16
  enable_js_formulas: false
  formula_folder_path: /
  inline_default: false
  inline_new_position: last_field
  date_format: yyyy-MM-dd
  datetime_format: "yyyy-MM-dd HH:mm:ss"
  metadata_date_format: "yyyy-MM-dd HH:mm:ss"
  enable_footer: false
  implementation: default
filters:
  enabled: false
  conditions:
```